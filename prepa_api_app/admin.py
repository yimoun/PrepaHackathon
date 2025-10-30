# admin.py
from django.contrib import admin
from django.utils.html import format_html
from django.db.models import Count, Q
from django.utils.safestring import mark_safe
from django.contrib import messages
from django.utils import timezone
from datetime import timedelta
from django.http import HttpResponse
import csv

from .models import Employe, Technicien, ModeleIA, Alerte


# ============================================================================
# FILTRES PERSONNALISÉS
# ============================================================================

class ActiveFilterModeleIA(admin.SimpleListFilter):
    """Filtre pour les modèles actifs/inactifs"""
    title = 'Statut d\'activation'
    parameter_name = 'active'

    def lookups(self, request, model_admin):
        return (
            ('active', 'Actifs seulement'),
            ('inactive', 'Inactifs seulement'),
        )

    def queryset(self, request, queryset):
        if self.value() == 'active':
            return queryset.filter(active=True)
        if self.value() == 'inactive':
            return queryset.filter(active=False)


class AlerteNonTraiteeFilter(admin.SimpleListFilter):
    """Filtre pour les alertes non traitées"""
    title = 'État de traitement'
    parameter_name = 'traitement'

    def lookups(self, request, model_admin):
        return (
            ('non_traite', 'Non traitées'),
            ('en_cours', 'En cours'),
            ('traite', 'Traitées'),
            ('urgent', 'Urgentes (>24h)'),
        )

    def queryset(self, request, queryset):
        if self.value() == 'non_traite':
            return queryset.filter(statut='NOUVEAU')
        if self.value() == 'en_cours':
            return queryset.filter(statut='EN_COURS')
        if self.value() == 'traite':
            return queryset.filter(statut__in=['RESOLU', 'IGNORE'])
        if self.value() == 'urgent':
            limite = timezone.now() - timedelta(hours=24)
            return queryset.filter(statut='NOUVEAU', created_at__lt=limite)


class NiveauGraviteFilter(admin.SimpleListFilter):
    """Filtre par niveau de gravité"""
    title = 'Niveau de gravité'
    parameter_name = 'niveau'

    def lookups(self, request, model_admin):
        return (
            ('CRITIQUE', 'Critique'),
            ('ELEVE', 'Élevé'),
            ('MOYEN', 'Moyen'),
            ('FAIBLE', 'Faible'),
        )

    def queryset(self, request, queryset):
        if self.value():
            return queryset.filter(niveau=self.value())


# ============================================================================
# INLINE ADMIN
# ============================================================================

class TechnicienInline(admin.TabularInline):
    """Inline pour afficher les techniciens d'un employé"""
    model = Technicien
    extra = 0
    fields = ['role', 'created_at']
    readonly_fields = ['created_at']
    can_delete = True
    verbose_name = "Rôle technique"
    verbose_name_plural = "Rôles techniques"


class AlerteInlineEmploye(admin.TabularInline):
    """Inline pour afficher les alertes d'un employé"""
    model = Alerte
    extra = 0
    fields = ['statut', 'niveau', 'typeEpiManquants', 'created_at', 'image_miniature']
    readonly_fields = ['image_miniature', 'created_at', 'typeEpiManquants']
    max_num = 5
    can_delete = False
    verbose_name = "Alerte récente"
    verbose_name_plural = "5 dernières alertes"

    def image_miniature(self, obj):
        if obj.image:
            return format_html(
                '<img src="{}" width="50" height="50" style="object-fit: cover; border-radius: 4px;" />',
                obj.image.url
            )
        return "Pas d'image"

    image_miniature.short_description = 'Image'

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.order_by('-created_at')[:5]


class AlerteInlineModeleIA(admin.TabularInline):
    """Inline pour afficher les alertes d'un modèle IA"""
    model = Alerte
    extra = 0
    fields = ['employee', 'statut', 'niveau', 'created_at']
    readonly_fields = ['employee', 'statut', 'niveau', 'created_at']
    max_num = 10
    can_delete = False
    verbose_name = "Alerte générée"
    verbose_name_plural = "10 dernières alertes générées"

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.order_by('-created_at')[:10]


# ============================================================================
# ADMIN EMPLOYE
# ============================================================================

@admin.register(Employe)
class EmployeAdmin(admin.ModelAdmin):
    list_display = [
        'id',
        'nom_complet_badge',
        'poste',
        'department',
        'status_badge',
        'nombre_alertes_badge',
        'alertes_non_traitees_badge',
        'derniere_alerte_info',
    ]
    list_filter = ['status', 'department', 'poste', 'created_at']
    search_fields = ['name', 'surname', 'poste', 'department']
    list_per_page = 25
    date_hierarchy = 'created_at'

    readonly_fields = [
        'created_at',
        'updated_at',
        'statistiques_alertes_display',
        'graphique_alertes',
        'timeline_alertes'
    ]

    fieldsets = (
        ('👤 Informations Personnelles', {
            'fields': ('user', 'name', 'surname')
        }),
        ('💼 Informations Professionnelles', {
            'fields': ('poste', 'department', 'status')
        }),
        ('📊 Statistiques et Alertes', {
            'fields': ('statistiques_alertes_display', 'graphique_alertes'),
            'classes': ('wide',)
        }),
        ('📅 Historique', {
            'fields': ('timeline_alertes',),
            'classes': ('collapse',)
        }),
        ('🕐 Métadonnées', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    inlines = [TechnicienInline, AlerteInlineEmploye]

    actions = ['activer_employes', 'desactiver_employes', 'exporter_rapport_csv']

    def nom_complet_badge(self, obj):
        """Affiche le nom complet avec avatar coloré"""
        couleurs = ['#FF6B6B', '#4ECDC4', '#45B7D1', '#FFA07A', '#98D8C8', '#F7DC6F']
        index_couleur = hash(obj.name) % len(couleurs)
        couleur = couleurs[index_couleur]

        return format_html(
            '<div style="display: flex; align-items: center; gap: 10px;">'
            '<div style="width: 35px; height: 35px; border-radius: 50%; background: {}; '
            'color: white; display: flex; align-items: center; justify-content: center; '
            'font-weight: bold; font-size: 14px; box-shadow: 0 2px 4px rgba(0,0,0,0.1);">{}</div>'
            '<div style="display: flex; flex-direction: column;">'
            '<span style="font-weight: 600; font-size: 13px;">{} {}</span>'
            '<span style="font-size: 11px; color: #666;">ID: {}</span>'
            '</div>'
            '</div>',
            couleur,
            obj.name[0].upper() if obj.name else '?',
            obj.name,
            obj.surname,
            obj.id
        )

    nom_complet_badge.short_description = 'Employé'

    def status_badge(self, obj):
        """Badge coloré pour le statut"""
        styles = {
            'ACTIF': ('linear-gradient(135deg, #667eea 0%, #764ba2 100%)', '✓', 'white'),
            'INACTIF': ('linear-gradient(135deg, #9E9E9E 0%, #616161 100%)', '✗', 'white'),
            'CONGE': ('linear-gradient(135deg, #f093fb 0%, #f5576c 100%)', '⌚', 'white'),
            'RETRAITE': ('linear-gradient(135deg, #4facfe 0%, #00f2fe 100%)', '→', 'white'),
        }
        bg, icon, color = styles.get(obj.status, ('#000', '?', 'white'))
        return format_html(
            '<span style="background: {}; color: {}; padding: 5px 12px; '
            'border-radius: 15px; font-size: 11px; font-weight: 600; '
            'box-shadow: 0 2px 4px rgba(0,0,0,0.15); display: inline-block;">'
            '{} {}</span>',
            bg, color, icon, obj.get_status_display()
        )

    status_badge.short_description = 'Statut'

    def nombre_alertes_badge(self, obj):
        """Nombre total d'alertes avec badge"""
        count = obj.alertes.count()
        critique = obj.alertes.filter(niveau='CRITIQUE').count()

        if critique > 0:
            color = 'linear-gradient(135deg, #fa709a 0%, #fee140 100%)'
            icon = '🔥'
        elif count > 10:
            color = 'linear-gradient(135deg, #a8edea 0%, #fed6e3 100%)'
            icon = '📊'
        else:
            color = 'linear-gradient(135deg, #e0c3fc 0%, #8ec5fc 100%)'
            icon = '📋'

        return format_html(
            '<div style="text-align: center;">'
            '<span style="background: {}; color: white; padding: 4px 12px; '
            'border-radius: 12px; font-size: 12px; font-weight: 700; '
            'box-shadow: 0 2px 4px rgba(0,0,0,0.15);">{} {}</span>'
            '{}'
            '</div>',
            color, icon, count,
            format_html('<div style="font-size: 10px; color: #f44336; margin-top: 2px;">⚠ {} critique(s)</div>',
                        critique) if critique > 0 else ''
        )

    nombre_alertes_badge.short_description = 'Total Alertes'

    def alertes_non_traitees_badge(self, obj):
        """Alertes en attente avec animation"""
        nouveau = obj.alertes.filter(statut='NOUVEAU').count()
        en_cours = obj.alertes.filter(statut='EN_COURS').count()

        if nouveau > 0:
            return format_html(
                '<div style="text-align: center;">'
                '<span style="background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%); '
                'color: white; padding: 4px 10px; border-radius: 12px; '
                'font-size: 12px; font-weight: 700; box-shadow: 0 2px 4px rgba(244,67,54,0.3); '
                'animation: pulse 2s infinite;">⚠ {} nouveau(x)</span>'
                '</div>',
                nouveau
            )
        elif en_cours > 0:
            return format_html(
                '<span style="background: linear-gradient(135deg, #ffecd2 0%, #fcb69f 100%); '
                'color: #333; padding: 4px 10px; border-radius: 12px; font-size: 11px; '
                'font-weight: 600;">⏳ {} en cours</span>',
                en_cours
            )
        return format_html('<span style="color: #4CAF50; font-size: 18px;">✓</span>')

    alertes_non_traitees_badge.short_description = 'À traiter'

    def derniere_alerte_info(self, obj):
        """Info sur la dernière alerte"""
        alerte = obj.alertes.order_by('-created_at').first()
        if alerte:
            delta = timezone.now() - alerte.created_at
            if delta.days == 0:
                if delta.seconds < 3600:
                    temps = f"{delta.seconds // 60} min"
                    color = '#f44336'
                else:
                    temps = f"{delta.seconds // 3600}h"
                    color = '#FF9800'
            elif delta.days == 1:
                temps = "Hier"
                color = '#FF9800'
            else:
                temps = f"{delta.days}j"
                color = '#757575'

            niveau_icons = {
                'CRITIQUE': '🔴',
                'ELEVE': '🟠',
                'MOYEN': '🟡',
                'FAIBLE': '🟢'
            }
            icon = niveau_icons.get(alerte.niveau, '⚪')

            return format_html(
                '<div style="font-size: 11px; text-align: center;">'
                '<div style="color: {}; font-weight: 600;">{}</div>'
                '<div style="color: #666; margin-top: 2px;">{} {}</div>'
                '</div>',
                color, temps, icon, alerte.get_niveau_display()
            )
        return format_html('<span style="color: #9E9E9E;">Aucune</span>')

    derniere_alerte_info.short_description = 'Dernière'

    def statistiques_alertes_display(self, obj):
        """Affichage des statistiques avec design moderne"""
        alertes = obj.alertes.all()
        total = alertes.count()

        if total == 0:
            return format_html(
                '<div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); '
                'color: white; padding: 30px; border-radius: 12px; text-align: center; '
                'box-shadow: 0 4px 6px rgba(0,0,0,0.1);">'
                '<div style="font-size: 48px; margin-bottom: 10px;">📊</div>'
                '<div style="font-size: 18px; font-weight: 600;">Aucune alerte enregistrée</div>'
                '<div style="font-size: 14px; opacity: 0.9; margin-top: 5px;">Cet employé n\'a pas d\'historique d\'alertes</div>'
                '</div>'
            )

        stats_statut = {
            'NOUVEAU': alertes.filter(statut='NOUVEAU').count(),
            'EN_COURS': alertes.filter(statut='EN_COURS').count(),
            'RESOLU': alertes.filter(statut='RESOLU').count(),
            'IGNORE': alertes.filter(statut='IGNORE').count(),
        }

        stats_niveau = {
            'CRITIQUE': alertes.filter(niveau='CRITIQUE').count(),
            'ELEVE': alertes.filter(niveau='ELEVE').count(),
            'MOYEN': alertes.filter(niveau='MOYEN').count(),
            'FAIBLE': alertes.filter(niveau='FAIBLE').count(),
        }

        taux_resolution = (stats_statut['RESOLU'] / total * 100) if total > 0 else 0

        html = f'''
        <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
                    padding: 25px; border-radius: 12px; color: white; 
                    box-shadow: 0 4px 15px rgba(0,0,0,0.2);">
            <h2 style="margin: 0 0 20px 0; font-size: 22px; font-weight: 700;">
                📊 Tableau de Bord des Alertes
            </h2>

            <div style="display: grid; grid-template-columns: repeat(3, 1fr); gap: 15px; margin-bottom: 20px;">
                <div style="background: rgba(255,255,255,0.15); padding: 15px; border-radius: 8px; 
                            backdrop-filter: blur(10px); text-align: center;">
                    <div style="font-size: 32px; font-weight: 800; margin-bottom: 5px;">{total}</div>
                    <div style="font-size: 12px; opacity: 0.9;">Total</div>
                </div>
                <div style="background: rgba(255,255,255,0.15); padding: 15px; border-radius: 8px; 
                            backdrop-filter: blur(10px); text-align: center;">
                    <div style="font-size: 32px; font-weight: 800; margin-bottom: 5px; color: #f44336;">
                        {stats_statut['NOUVEAU']}
                    </div>
                    <div style="font-size: 12px; opacity: 0.9;">Non traitées</div>
                </div>
                <div style="background: rgba(255,255,255,0.15); padding: 15px; border-radius: 8px; 
                            backdrop-filter: blur(10px); text-align: center;">
                    <div style="font-size: 32px; font-weight: 800; margin-bottom: 5px; color: #4CAF50;">
                        {taux_resolution:.0f}%
                    </div>
                    <div style="font-size: 12px; opacity: 0.9;">Taux de résolution</div>
                </div>
            </div>

            <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 20px;">
                <div style="background: rgba(255,255,255,0.1); padding: 15px; border-radius: 8px; 
                            backdrop-filter: blur(10px);">
                    <h3 style="margin: 0 0 12px 0; font-size: 14px; font-weight: 600; opacity: 0.9;">
                        Par Statut
                    </h3>
                    <div style="display: flex; flex-direction: column; gap: 8px;">
                        <div style="display: flex; justify-content: space-between; align-items: center;">
                            <span style="font-size: 13px;">🆕 Nouveau</span>
                            <span style="background: rgba(33,150,243,0.3); padding: 2px 10px; 
                                        border-radius: 10px; font-size: 12px; font-weight: 600;">
                                {stats_statut['NOUVEAU']}
                            </span>
                        </div>
                        <div style="display: flex; justify-content: space-between; align-items: center;">
                            <span style="font-size: 13px;">⏳ En cours</span>
                            <span style="background: rgba(255,152,0,0.3); padding: 2px 10px; 
                                        border-radius: 10px; font-size: 12px; font-weight: 600;">
                                {stats_statut['EN_COURS']}
                            </span>
                        </div>
                        <div style="display: flex; justify-content: space-between; align-items: center;">
                            <span style="font-size: 13px;">✅ Résolu</span>
                            <span style="background: rgba(76,175,80,0.3); padding: 2px 10px; 
                                        border-radius: 10px; font-size: 12px; font-weight: 600;">
                                {stats_statut['RESOLU']}
                            </span>
                        </div>
                        <div style="display: flex; justify-content: space-between; align-items: center;">
                            <span style="font-size: 13px;">🚫 Ignoré</span>
                            <span style="background: rgba(158,158,158,0.3); padding: 2px 10px; 
                                        border-radius: 10px; font-size: 12px; font-weight: 600;">
                                {stats_statut['IGNORE']}
                            </span>
                        </div>
                    </div>
                </div>

                <div style="background: rgba(255,255,255,0.1); padding: 15px; border-radius: 8px; 
                            backdrop-filter: blur(10px);">
                    <h3 style="margin: 0 0 12px 0; font-size: 14px; font-weight: 600; opacity: 0.9;">
                        Par Niveau de Gravité
                    </h3>
                    <div style="display: flex; flex-direction: column; gap: 8px;">
                        <div style="display: flex; justify-content: space-between; align-items: center;">
                            <span style="font-size: 13px;">🔴 Critique</span>
                            <span style="background: rgba(244,67,54,0.4); padding: 2px 10px; 
                                        border-radius: 10px; font-size: 12px; font-weight: 600;">
                                {stats_niveau['CRITIQUE']}
                            </span>
                        </div>
                        <div style="display: flex; justify-content: space-between; align-items: center;">
                            <span style="font-size: 13px;">🟠 Élevé</span>
                            <span style="background: rgba(255,152,0,0.4); padding: 2px 10px; 
                                        border-radius: 10px; font-size: 12px; font-weight: 600;">
                                {stats_niveau['ELEVE']}
                            </span>
                        </div>
                        <div style="display: flex; justify-content: space-between; align-items: center;">
                            <span style="font-size: 13px;">🟡 Moyen</span>
                            <span style="background: rgba(255,235,59,0.4); padding: 2px 10px; 
                                        border-radius: 10px; font-size: 12px; font-weight: 600;">
                                {stats_niveau['MOYEN']}
                            </span>
                        </div>
                        <div style="display: flex; justify-content: space-between; align-items: center;">
                            <span style="font-size: 13px;">🟢 Faible</span>
                            <span style="background: rgba(76,175,80,0.4); padding: 2px 10px; 
                                        border-radius: 10px; font-size: 12px; font-weight: 600;">
                                {stats_niveau['FAIBLE']}
                            </span>
                        </div>
                    </div>
                </div>
            </div>
        </div>
        '''
        return mark_safe(html)

    statistiques_alertes_display.short_description = 'Vue d\'ensemble'

    def graphique_alertes(self, obj):
        """Graphique visuel des alertes sur 7 jours"""
        from datetime import timedelta

        alertes = obj.alertes.all()
        if not alertes.exists():
            return "Pas de données"

        # Préparer les données pour les 7 derniers jours
        aujourdhui = timezone.now().date()
        donnees_jours = []

        for i in range(6, -1, -1):
            jour = aujourdhui - timedelta(days=i)
            count = alertes.filter(
                created_at__date=jour
            ).count()
            donnees_jours.append((jour, count))

        max_count = max([c for _, c in donnees_jours]) if donnees_jours else 1

        barres_html = ''
        for jour, count in donnees_jours:
            hauteur = (count / max_count * 100) if max_count > 0 else 0
            jour_fr = ['Lun', 'Mar', 'Mer', 'Jeu', 'Ven', 'Sam', 'Dim'][jour.weekday()]

            color = '#f44336' if count > 5 else '#FF9800' if count > 2 else '#4CAF50'

            barres_html += f'''
            <div style="display: flex; flex-direction: column; align-items: center; flex: 1;">
                <div style="position: relative; height: 120px; display: flex; align-items: flex-end; width: 100%;">
                    <div style="width: 100%; background: {color}; border-radius: 4px 4px 0 0; 
                                height: {hauteur}%; position: relative; transition: all 0.3s ease;
                                box-shadow: 0 -2px 4px rgba(0,0,0,0.1);">
                        {f'<span style="position: absolute; top: -20px; left: 50%; transform: translateX(-50%); font-size: 11px; font-weight: 600; color: #333;">{count}</span>' if count > 0 else ''}
                    </div>
                </div>
                <div style="margin-top: 8px; font-size: 11px; font-weight: 500; color: #666;">
                    {jour_fr}
                </div>
                <div style="font-size: 9px; color: #999;">
                    {jour.strftime('%d/%m')}
                </div>
            </div>
            '''

        html = f'''
        <div style="background: white; padding: 20px; border-radius: 12px; 
                    box-shadow: 0 2px 8px rgba(0,0,0,0.1);">
            <h3 style="margin: 0 0 15px 0; font-size: 16px; font-weight: 600; color: #333;">
                📈 Activité des 7 derniers jours
            </h3>
            <div style="display: flex; gap: 8px; align-items: flex-end; padding: 10px 0;">
                {barres_html}
            </div>
            <div style="margin-top: 15px; padding-top: 15px; border-top: 1px solid #eee; 
                        display: flex; justify-content: space-between; font-size: 12px;">
                <span style="color: #666;">
                    <strong>Total période:</strong> {sum([c for _, c in donnees_jours])} alertes
                </span>
                <span style="color: #666;">
                    <strong>Moyenne/jour:</strong> {sum([c for _, c in donnees_jours]) / 7:.1f}
                </span>
            </div>
        </div>
        '''
        return mark_safe(html)

    graphique_alertes.short_description = 'Tendance hebdomadaire'

    def timeline_alertes(self, obj):
        """Timeline des 15 dernières alertes"""
        alertes = obj.alertes.order_by('-created_at')[:15]

        if not alertes.exists():
            return "Aucune alerte dans l'historique"

        timeline_html = ''
        for alerte in alertes:
            niveau_styles = {
                'CRITIQUE': ('#f44336', '🔴'),
                'ELEVE': ('#FF9800', '🟠'),
                'MOYEN': ('#FFEB3B', '🟡'),
                'FAIBLE': ('#4CAF50', '🟢'),
            }
            color, icon = niveau_styles.get(alerte.niveau, ('#666', '⚪'))

            statut_styles = {
                'NOUVEAU': ('#2196F3', 'rgba(33, 150, 243, 0.1)'),
                'EN_COURS': ('#FF9800', 'rgba(255, 152, 0, 0.1)'),
                'RESOLU': ('#4CAF50', 'rgba(76, 175, 80, 0.1)'),
                'IGNORE': ('#9E9E9E', 'rgba(158, 158, 158, 0.1)'),
            }
            statut_color, statut_bg = statut_styles.get(alerte.statut, ('#666', '#f5f5f5'))

            delta = timezone.now() - alerte.created_at
            if delta.days == 0:
                if delta.seconds < 3600:
                    temps = f"Il y a {delta.seconds // 60} minutes"
                else:
                    temps = f"Il y a {delta.seconds // 3600} heures"
            elif delta.days == 1:
                temps = "Hier"
            else:
                temps = f"Il y a {delta.days} jours"

            timeline_html += f'''
                            <div style="display: flex; gap: 15px; margin-bottom: 20px; position: relative;">
                <div style="display: flex; flex-direction: column; align-items: center;">
                    <div style="width: 40px; height: 40px; border-radius: 50%; background: {color}; 
                                color: white; display: flex; align-items: center; justify-content: center;
                                font-size: 20px; box-shadow: 0 2px 4px rgba(0,0,0,0.2); z-index: 2;">
                        {icon}
                    </div>
                    <div style="width: 2px; height: 100%; background: linear-gradient(to bottom, {color}, transparent); 
                                position: absolute; top: 40px; left: 19px;"></div>
                </div>
                <div style="flex: 1; background: {statut_bg}; padding: 15px; border-radius: 8px; 
                            border-left: 3px solid {statut_color};">
                    <div style="display: flex; justify-content: space-between; align-items: start; margin-bottom: 8px;">
                        <div>
                            <span style="font-weight: 600; color: #333; font-size: 13px;">
                                Alerte #{alerte.id}
                            </span>
                            <span style="background: {statut_color}; color: white; padding: 2px 8px; 
                                        border-radius: 10px; font-size: 10px; margin-left: 8px;">
                                {alerte.get_statut_display()}
                            </span>
                        </div>
                        <span style="font-size: 11px; color: #666;">{temps}</span>
                    </div>
                    <div style="font-size: 12px; color: #666; margin-bottom: 5px;">
                        <strong>EPI manquants:</strong> {alerte.typeEpiManquants[:100]}{'...' if len(alerte.typeEpiManquants) > 100 else ''}
                    </div>
                    <div style="font-size: 11px; color: #999;">
                        📅 {alerte.created_at.strftime('%d/%m/%Y à %H:%M')} | 
                        🤖 {alerte.modeleIA.name}
                    </div>
                </div>
            </div>
            '''

        html = f'''
        <div style="background: white; padding: 20px; border-radius: 12px; 
                    box-shadow: 0 2px 8px rgba(0,0,0,0.1); max-height: 600px; overflow-y: auto;">
            <h3 style="margin: 0 0 20px 0; font-size: 16px; font-weight: 600; color: #333;">
                🕐 Historique des 15 dernières alertes
            </h3>
            {timeline_html}
        </div>
        '''
        return mark_safe(html)

    timeline_alertes.short_description = 'Timeline des alertes'

    # Actions personnalisées
    def activer_employes(self, request, queryset):
        count = queryset.update(status='ACTIF')
        self.message_user(request, f'{count} employé(s) activé(s) avec succès.', messages.SUCCESS)

    activer_employes.short_description = "✅ Activer les employés sélectionnés"

    def desactiver_employes(self, request, queryset):
        count = queryset.update(status='INACTIF')
        self.message_user(request, f'{count} employé(s) désactivé(s) avec succès.', messages.WARNING)

    desactiver_employes.short_description = "❌ Désactiver les employés sélectionnés"

    def exporter_rapport_csv(self, request, queryset):
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="rapport_employes.csv"'
        response.write('\ufeff')  # BOM pour Excel

        writer = csv.writer(response, delimiter=';')
        writer.writerow(['ID', 'Nom', 'Prénom', 'Poste', 'Département', 'Statut',
                         'Total Alertes', 'Alertes Non Traitées', 'Alertes Critiques'])

        for employe in queryset:
            writer.writerow([
                employe.id,
                employe.name,
                employe.surname,
                employe.poste,
                employe.department,
                employe.get_status_display(),
                employe.alertes.count(),
                employe.alertes.filter(statut='NOUVEAU').count(),
                employe.alertes.filter(niveau='CRITIQUE').count(),
            ])

        self.message_user(request, f'Rapport CSV généré pour {queryset.count()} employé(s).', messages.SUCCESS)
        return response

    exporter_rapport_csv.short_description = "📥 Exporter en CSV"


# ============================================================================
# ADMIN TECHNICIEN
# ============================================================================

@admin.register(Technicien)
class TechnicienAdmin(admin.ModelAdmin):
    list_display = ['id', 'nom_technicien', 'role_badge', 'employe_info', 'created_at']
    list_filter = ['role', 'created_at']
    search_fields = ['employee__name', 'employee__surname', 'role']
    list_per_page = 25
    date_hierarchy = 'created_at'

    fieldsets = (
        ('👤 Identité', {
            'fields': ('employee',)
        }),
        ('🔧 Rôle Technique', {
            'fields': ('role',)
        }),
        ('🕐 Métadonnées', {
            'fields': ('created_at',),
            'classes': ('collapse',)
        }),
    )

    readonly_fields = ['created_at']

    def nom_technicien(self, obj):
        return format_html(
            '<div style="display: flex; align-items: center; gap: 10px;">'
            '<div style="width: 30px; height: 30px; border-radius: 50%; background: #FF5722; '
            'color: white; display: flex; align-items: center; justify-content: center; '
            'font-weight: bold; font-size: 12px;">🔧</div>'
            '<span style="font-weight: 600;">{} {}</span>'
            '</div>',
            obj.employee.name,
            obj.employee.surname
        )

    nom_technicien.short_description = 'Technicien'

    def role_badge(self, obj):
        styles = {
            'SUPPORT': ('linear-gradient(135deg, #667eea 0%, #764ba2 100%)', '💬'),
            'MAINTENANCE': ('linear-gradient(135deg, #f093fb 0%, #f5576c 100%)', '🔧'),
            'RESEAU': ('linear-gradient(135deg, #4facfe 0%, #00f2fe 100%)', '🌐'),
            'SECURITE': ('linear-gradient(135deg, #43e97b 0%, #38f9d7 100%)', '🔒'),
        }
        bg, icon = styles.get(obj.role, ('#000', '?'))
        return format_html(
            '<span style="background: {}; color: white; padding: 5px 12px; '
            'border-radius: 15px; font-size: 11px; font-weight: 600;">{} {}</span>',
            bg, icon, obj.get_role_display()
        )

    role_badge.short_description = 'Rôle'

    def employe_info(self, obj):
        return format_html(
            '<div style="font-size: 11px;">'
            '<div style="color: #333; font-weight: 500;">{}</div>'
            '<div style="color: #666;">{}</div>'
            '</div>',
            obj.employee.poste,
            obj.employee.department
        )

    employe_info.short_description = 'Poste / Département'


# ============================================================================
# ADMIN MODELE IA
# ============================================================================

@admin.register(ModeleIA)
class ModeleIAAdmin(admin.ModelAdmin):
    list_display = [
        'id',
        'nom_version_badge',
        'sensibilite_gauge',
        'types_epi_display',
        'active_toggle',
        'nombre_alertes_generees',
        'taux_precision',
        'created_at'
    ]
    list_filter = [ActiveFilterModeleIA, 'created_at']
    search_fields = ['name', 'version', 'typesEpi']
    list_per_page = 20
    date_hierarchy = 'created_at'

    readonly_fields = [
        'created_at',
        'statistiques_modele',
        'performance_analysis',
        'alertes_recentes_display'
    ]

    fieldsets = (
        ('🤖 Informations du Modèle', {
            'fields': ('name', 'version', 'active')
        }),
        ('⚙️ Configuration', {
            'fields': ('sensibilite', 'typesEpi')
        }),
        ('📊 Performance', {
            'fields': ('statistiques_modele', 'performance_analysis'),
            'classes': ('wide',)
        }),
        ('🔔 Alertes Générées', {
            'fields': ('alertes_recentes_display',),
            'classes': ('collapse',)
        }),
        ('🕐 Métadonnées', {
            'fields': ('created_at',),
            'classes': ('collapse',)
        }),
    )

    inlines = [AlerteInlineModeleIA]

    actions = ['activer_modele', 'desactiver_modele', 'dupliquer_modele']

    def nom_version_badge(self, obj):
        return format_html(
            '<div style="display: flex; align-items: center; gap: 10px;">'
            '<div style="width: 35px; height: 35px; border-radius: 8px; '
            'background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); '
            'color: white; display: flex; align-items: center; justify-content: center; '
            'font-size: 16px; box-shadow: 0 2px 4px rgba(0,0,0,0.1);">🤖</div>'
            '<div>'
            '<div style="font-weight: 600; font-size: 13px; color: #333;">{}</div>'
            '<div style="font-size: 11px; color: #666;">Version {}</div>'
            '</div>'
            '</div>',
            obj.name,
            obj.version
        )

    nom_version_badge.short_description = 'Modèle IA'

    def sensibilite_gauge(self, obj):
        """Jauge de sensibilité visuelle"""
        pourcentage = obj.sensibilite

        if pourcentage < 30:
            color = '#4CAF50'
            label = 'Faible'
        elif pourcentage < 70:
            color = '#FF9800'
            label = 'Moyenne'
        else:
            color = '#f44336'
            label = 'Élevée'

        return format_html(
            '<div style="width: 120px;">'
            '<div style="display: flex; justify-content: space-between; margin-bottom: 4px; font-size: 11px;">'
            '<span style="color: #666;">{}</span>'
            '<span style="font-weight: 600; color: {};">{}</span>'
            '</div>'
            '<div style="width: 100%; height: 8px; background: #e0e0e0; border-radius: 4px; overflow: hidden;">'
            '<div style="width: {}%; height: 100%; background: {}; transition: width 0.3s ease;"></div>'
            '</div>'
            '</div>',
            label, color, pourcentage, pourcentage, color
        )

    sensibilite_gauge.short_description = 'Sensibilité'

    def types_epi_display(self, obj):
        """Affichage des types d'EPI sous forme de tags"""
        types = [t.strip() for t in obj.typesEpi.split(',')]
        tags_html = ''

        colors = ['#2196F3', '#4CAF50', '#FF9800', '#9C27B0', '#F44336', '#00BCD4']

        for i, type_epi in enumerate(types[:5]):  # Limite à 5 pour l'affichage
            color = colors[i % len(colors)]
            tags_html += f'''
            <span style="background: {color}; color: white; padding: 3px 8px; 
                        border-radius: 10px; font-size: 10px; margin-right: 4px; 
                        display: inline-block; margin-bottom: 4px;">{type_epi}</span>
            '''

        if len(types) > 5:
            tags_html += f'<span style="color: #666; font-size: 10px;">+{len(types) - 5} autres</span>'

        return format_html(tags_html)

    types_epi_display.short_description = 'Types EPI détectés'

    def active_toggle(self, obj):
        """Toggle visuel pour l'état actif"""
        if obj.active:
            return format_html(
                '<div style="display: flex; align-items: center; gap: 8px;">'
                '<div style="width: 40px; height: 20px; background: #4CAF50; border-radius: 10px; '
                'position: relative; box-shadow: inset 0 1px 3px rgba(0,0,0,0.2);">'
                '<div style="width: 16px; height: 16px; background: white; border-radius: 50%; '
                'position: absolute; right: 2px; top: 2px; box-shadow: 0 1px 2px rgba(0,0,0,0.3);"></div>'
                '</div>'
                '<span style="color: #4CAF50; font-weight: 600; font-size: 11px;">✓ ACTIF</span>'
                '</div>'
            )
        else:
            return format_html(
                '<div style="display: flex; align-items: center; gap: 8px;">'
                '<div style="width: 40px; height: 20px; background: #ccc; border-radius: 10px; '
                'position: relative; box-shadow: inset 0 1px 3px rgba(0,0,0,0.2);">'
                '<div style="width: 16px; height: 16px; background: white; border-radius: 50%; '
                'position: absolute; left: 2px; top: 2px; box-shadow: 0 1px 2px rgba(0,0,0,0.3);"></div>'
                '</div>'
                '<span style="color: #999; font-weight: 600; font-size: 11px;">✗ INACTIF</span>'
                '</div>'
            )

    active_toggle.short_description = 'Statut'

    def nombre_alertes_generees(self, obj):
        """Nombre d'alertes générées par ce modèle"""
        total = obj.alertes.count()
        nouveau = obj.alertes.filter(statut='NOUVEAU').count()

        return format_html(
            '<div style="text-align: center;">'
            '<div style="font-size: 18px; font-weight: 700; color: #2196F3;">{}</div>'
            '<div style="font-size: 10px; color: #666;">alertes</div>'
            '{}'
            '</div>',
            total,
            format_html('<div style="font-size: 9px; color: #f44336; margin-top: 2px;">⚠ {} nouvelles</div>',
                        nouveau) if nouveau > 0 else ''
        )

    nombre_alertes_generees.short_description = 'Alertes'

    def taux_precision(self, obj):
        """Calcul du taux de précision basé sur les faux positifs"""
        total = obj.alertes.count()
        if total == 0:
            return format_html('<span style="color: #999;">N/A</span>')

        resolu = obj.alertes.filter(statut='RESOLU').count()
        ignore = obj.alertes.filter(statut='IGNORE').count()

        # Précision = (alertes résolues + ignorées) / total
        precision = ((resolu + ignore) / total) * 100

        if precision >= 80:
            color = '#4CAF50'
            icon = '🟢'
        elif precision >= 60:
            color = '#FF9800'
            icon = '🟡'
        else:
            color = '#f44336'
            icon = '🔴'

        return format_html(
            '<span style="color: {}; font-weight: 600; font-size: 13px;">{} {:.0f}%</span>',
            color, icon, precision
        )

    taux_precision.short_description = 'Précision'

    def statistiques_modele(self, obj):
        """Statistiques détaillées du modèle"""
        alertes = obj.alertes.all()
        total = alertes.count()

        if total == 0:
            return format_html(
                '<div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); '
                'color: white; padding: 30px; border-radius: 12px; text-align: center;">'
                '<div style="font-size: 48px; margin-bottom: 10px;">🤖</div>'
                '<div style="font-size: 18px; font-weight: 600;">Aucune alerte générée</div>'
                '<div style="font-size: 14px; opacity: 0.9; margin-top: 5px;">Ce modèle n\'a pas encore été utilisé</div>'
                '</div>'
            )

        stats = {
            'nouveau': alertes.filter(statut='NOUVEAU').count(),
            'en_cours': alertes.filter(statut='EN_COURS').count(),
            'resolu': alertes.filter(statut='RESOLU').count(),
            'ignore': alertes.filter(statut='IGNORE').count(),
        }

        niveaux = {
            'CRITIQUE': alertes.filter(niveau='CRITIQUE').count(),
            'ELEVE': alertes.filter(niveau='ELEVE').count(),
            'MOYEN': alertes.filter(niveau='MOYEN').count(),
            'FAIBLE': alertes.filter(niveau='FAIBLE').count(),
        }

        taux_traitement = ((stats['resolu'] + stats['ignore']) / total * 100) if total > 0 else 0

        # Employés les plus alertés
        top_employes = alertes.values(
            'employee__name', 'employee__surname'
        ).annotate(
            count=Count('id')
        ).order_by('-count')[:5]

        top_html = ''
        for emp in top_employes:
            top_html += f'''
            <div style="display: flex; justify-content: space-between; padding: 5px 0; 
                        border-bottom: 1px solid rgba(255,255,255,0.1);">
                <span style="font-size: 12px;">{emp['employee__name']} {emp['employee__surname']}</span>
                <span style="background: rgba(255,255,255,0.2); padding: 2px 8px; 
                            border-radius: 10px; font-size: 11px; font-weight: 600;">{emp['count']}</span>
            </div>
            '''

        html = f'''
        <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
                    padding: 25px; border-radius: 12px; color: white;">
            <h2 style="margin: 0 0 20px 0; font-size: 22px; font-weight: 700;">
                📊 Statistiques du Modèle
            </h2>

            <div style="display: grid; grid-template-columns: repeat(4, 1fr); gap: 12px; margin-bottom: 20px;">
                <div style="background: rgba(255,255,255,0.15); padding: 15px; border-radius: 8px; text-align: center;">
                    <div style="font-size: 28px; font-weight: 800;">{total}</div>
                    <div style="font-size: 11px; opacity: 0.9;">Total</div>
                </div>
                <div style="background: rgba(255,255,255,0.15); padding: 15px; border-radius: 8px; text-align: center;">
                    <div style="font-size: 28px; font-weight: 800; color: #FFE57F;">{stats['nouveau']}</div>
                    <div style="font-size: 11px; opacity: 0.9;">Nouveau</div>
                </div>
                <div style="background: rgba(255,255,255,0.15); padding: 15px; border-radius: 8px; text-align: center;">
                    <div style="font-size: 28px; font-weight: 800; color: #81C784;">{taux_traitement:.0f}%</div>
                    <div style="font-size: 11px; opacity: 0.9;">Traitement</div>
                </div>
                <div style="background: rgba(255,255,255,0.15); padding: 15px; border-radius: 8px; text-align: center;">
                    <div style="font-size: 28px; font-weight: 800; color: #FF8A80;">{niveaux['CRITIQUE']}</div>
                    <div style="font-size: 11px; opacity: 0.9;">Critiques</div>
                </div>
            </div>

            <div style="background: rgba(255,255,255,0.1); padding: 15px; border-radius: 8px;">
                <h3 style="margin: 0 0 12px 0; font-size: 14px; font-weight: 600;">
                    👥 Top 5 Employés Alertés
                </h3>
                {top_html if top_html else '<div style="font-size: 12px; opacity: 0.7;">Aucune donnée</div>'}
            </div>
        </div>
        '''
        return mark_safe(html)

    statistiques_modele.short_description = 'Vue d\'ensemble'

    def performance_analysis(self, obj):
        """Analyse de performance du modèle sur 30 jours"""
        from datetime import timedelta

        alertes_30j = obj.alertes.filter(
            created_at__gte=timezone.now() - timedelta(days=30)
        )

        total_30j = alertes_30j.count()
        if total_30j == 0:
            return "Pas de données sur les 30 derniers jours"

        # Répartition par semaine
        semaines_data = []
        for i in range(4):
            debut = timezone.now() - timedelta(days=(4 - i) * 7)
            fin = timezone.now() - timedelta(days=(3 - i) * 7)
            count = alertes_30j.filter(created_at__gte=debut, created_at__lt=fin).count()
            semaines_data.append(count)

        max_week = max(semaines_data) if semaines_data else 1

        barres_html = ''
        for i, count in enumerate(semaines_data):
            hauteur = (count / max_week * 100) if max_week > 0 else 0
            color = '#667eea'

            barres_html += f'''
            <div style="flex: 1; display: flex; flex-direction: column; align-items: center;">
                <div style="height: 100px; width: 100%; display: flex; align-items: flex-end; justify-content: center;">
                    <div style="width: 80%; background: {color}; height: {hauteur}%; 
                                border-radius: 4px 4px 0 0; position: relative;">
                        <span style="position: absolute; top: -20px; left: 50%; transform: translateX(-50%); 
                                    font-size: 12px; font-weight: 600; color: #333;">{count}</span>
                    </div>
                </div>
                <span style="font-size: 11px; color: #666; margin-top: 8px;">S{i + 1}</span>
            </div>
            '''

        moyenne_jour = total_30j / 30

        html = f'''
        <div style="background: white; padding: 20px; border-radius: 12px; box-shadow: 0 2px 8px rgba(0,0,0,0.1);">
            <h3 style="margin: 0 0 15px 0; font-size: 16px; font-weight: 600; color: #333;">
                📈 Performance sur 30 jours
            </h3>
            <div style="display: flex; gap: 10px; margin-bottom: 15px;">
                {barres_html}
            </div>
            <div style="display: flex; justify-content: space-around; padding-top: 15px; 
                        border-top: 1px solid #eee; font-size: 12px; color: #666;">
                <div><strong>Total:</strong> {total_30j} alertes</div>
                <div><strong>Moyenne/jour:</strong> {moyenne_jour:.1f}</div>
                <div><strong>Max/semaine:</strong> {max(semaines_data)}</div>
            </div>
        </div>
        '''
        return mark_safe(html)

    performance_analysis.short_description = 'Performance mensuelle'

    def alertes_recentes_display(self, obj):
        """Affichage des 10 dernières alertes"""
        alertes = obj.alertes.order_by('-created_at')[:10]

        if not alertes.exists():
            return "Aucune alerte générée"

        lignes_html = ''
        for alerte in alertes:
            niveau_colors = {
                'CRITIQUE': '#f44336',
                'ELEVE': '#FF9800',
                'MOYEN': '#FFEB3B',
                'FAIBLE': '#4CAF50',
            }
            color = niveau_colors.get(alerte.niveau, '#666')

            lignes_html += f'''
            <tr style="border-bottom: 1px solid #eee;">
                <td style="padding: 10px;">#{alerte.id}</td>
                <td style="padding: 10px;">{alerte.employee.name} {alerte.employee.surname}</td>
                <td style="padding: 10px;">
                    <span style="color: {color}; font-weight: 600;">●</span> {alerte.get_niveau_display()}
                </td>
                <td style="padding: 10px;">
                    <span style="background: #f5f5f5; padding: 3px 8px; border-radius: 10px; font-size: 11px;">
                        {alerte.get_statut_display()}
                    </span>
                </td>
                <td style="padding: 10px; font-size: 11px; color: #666;">
                    {alerte.created_at.strftime('%d/%m/%Y %H:%M')}
                </td>
            </tr>
            '''

        html = f'''
        <div style="background: white; border-radius: 8px; overflow: hidden; box-shadow: 0 2px 4px rgba(0,0,0,0.1);">
            <table style="width: 100%; border-collapse: collapse;">
                <thead>
                    <tr style="background: #f5f5f5;">
                        <th style="padding: 10px; text-align: left; font-size: 12px;">ID</th>
                        <th style="padding: 10px; text-align: left; font-size: 12px;">Employé</th>
                        <th style="padding: 10px; text-align: left; font-size: 12px;">Niveau</th>
                        <th style="padding: 10px; text-align: left; font-size: 12px;">Statut</th>
                        <th style="padding: 10px; text-align: left; font-size: 12px;">Date</th>
                    </tr>
                </thead>
                <tbody>
                    {lignes_html}
                </tbody>
            </table>
        </div>
        '''
        return mark_safe(html)

    alertes_recentes_display.short_description = 'Dernières alertes'

    # Actions
    def activer_modele(self, request, queryset):
        # Désactiver tous les autres modèles d'abord
        ModeleIA.objects.update(active=False)
        count = queryset.update(active=True)
        self.message_user(request, f'{count} modèle(s) activé(s). Les autres ont été désactivés.', messages.SUCCESS)


    activer_modele.short_description = "✅ Activer les modèles sélectionnés"

    def desactiver_modele(self, request, queryset):
        count = queryset.update(active=False)
        self.message_user(request, f'{count} modèle(s) désactivé(s).', messages.WARNING)

    desactiver_modele.short_description = "❌ Désactiver les modèles sélectionnés"

    def dupliquer_modele(self, request, queryset):
        count = 0
        for modele in queryset:
            modele.pk = None
            modele.name = f"{modele.name} (Copie)"
            modele.active = False
            modele.save()
            count += 1
        self.message_user(request, f'{count} modèle(s) dupliqué(s).', messages.SUCCESS)

    dupliquer_modele.short_description = "📋 Dupliquer les modèles sélectionnés"

    # ============================================================================
    # ADMIN ALERTE
    # ============================================================================

    @admin.register(Alerte)
    class AlerteAdmin(admin.ModelAdmin):
        list_display = [
            'id',
            'employe_badge',
            'modele_ia_badge',
            'niveau_badge',
            'statut_badge',
            'epis_manquants_preview',
            'image_preview',
            'created_at_display',
            'temps_ecoule'
        ]
        list_filter = [
            AlerteNonTraiteeFilter,
            NiveauGraviteFilter,
            'statut',
            'niveau',
            'created_at',
            'modeleIA'
        ]
        search_fields = [
            'employee__name',
            'employee__surname',
            'typeEpiManquants',
            'modeleIA__name'
        ]
        list_per_page = 30
        date_hierarchy = 'created_at'

        readonly_fields = [
            'created_at',
            'image_large',
            'employee',
            'modeleIA',
            'analyse_details'
        ]

        fieldsets = (
            ('🔔 Informations de l\'Alerte', {
                'fields': ('employee', 'modeleIA', 'statut', 'niveau')
            }),
            ('🦺 Détails EPI', {
                'fields': ('typeEpiManquants',)
            }),
            ('📸 Image Capturée', {
                'fields': ('image', 'image_large'),
                'classes': ('wide',)
            }),
            ('📊 Analyse', {
                'fields': ('analyse_details',),
                'classes': ('collapse',)
            }),
            ('🕐 Métadonnées', {
                'fields': ('created_at',),
                'classes': ('collapse',)
            }),
        )

        actions = [
            'marquer_resolu',
            'marquer_en_cours',
            'marquer_ignore',
            'changer_niveau_critique',
            'exporter_alertes_csv'
        ]

        def employe_badge(self, obj):
            """Badge de l'employé avec avatar"""
            couleurs = ['#FF6B6B', '#4ECDC4', '#45B7D1', '#FFA07A', '#98D8C8', '#F7DC6F']
            index_couleur = hash(obj.employee.name) % len(couleurs)
            couleur = couleurs[index_couleur]

            return format_html(
                '<div style="display: flex; align-items: center; gap: 8px;">'
                '<div style="width: 30px; height: 30px; border-radius: 50%; background: {}; '
                'color: white; display: flex; align-items: center; justify-content: center; '
                'font-weight: bold; font-size: 11px;">{}</div>'
                '<div style="display: flex; flex-direction: column;">'
                '<span style="font-weight: 600; font-size: 12px;">{} {}</span>'
                '<span style="font-size: 10px; color: #666;">{}</span>'
                '</div>'
                '</div>',
                couleur,
                obj.employee.name[0].upper() if obj.employee.name else '?',
                obj.employee.name,
                obj.employee.surname,
                obj.employee.poste
            )

        employe_badge.short_description = 'Employé'

        def modele_ia_badge(self, obj):
            """Badge du modèle IA"""
            return format_html(
                '<div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); '
                'color: white; padding: 5px 10px; border-radius: 8px; font-size: 11px; '
                'text-align: center; box-shadow: 0 2px 4px rgba(0,0,0,0.1);">'
                '<div style="font-weight: 600;">{}</div>'
                '<div style="font-size: 9px; opacity: 0.9;">v{}</div>'
                '</div>',
                obj.modeleIA.name,
                obj.modeleIA.version
            )

        modele_ia_badge.short_description = 'Modèle IA'

        def niveau_badge(self, obj):
            """Badge du niveau de gravité"""
            styles = {
                'CRITIQUE': ('linear-gradient(135deg, #f44336 0%, #e91e63 100%)', '🔴', 'white'),
                'ELEVE': ('linear-gradient(135deg, #FF9800 0%, #FF5722 100%)', '🟠', 'white'),
                'MOYEN': ('linear-gradient(135deg, #FFEB3B 0%, #FFC107 100%)', '🟡', '#333'),
                'FAIBLE': ('linear-gradient(135deg, #4CAF50 0%, #8BC34A 100%)', '🟢', 'white'),
            }
            bg, icon, color = styles.get(obj.niveau, ('#666', '⚪', 'white'))

            return format_html(
                '<span style="background: {}; color: {}; padding: 6px 12px; '
                'border-radius: 12px; font-size: 11px; font-weight: 600; '
                'box-shadow: 0 2px 4px rgba(0,0,0,0.15); display: inline-block;">'
                '{} {}</span>',
                bg, color, icon, obj.get_niveau_display()
            )

        niveau_badge.short_description = 'Niveau'

        def statut_badge(self, obj):
            """Badge du statut"""
            styles = {
                'NOUVEAU': ('linear-gradient(135deg, #2196F3 0%, #03A9F4 100%)', '🆕', 'white'),
                'EN_COURS': ('linear-gradient(135deg, #FF9800 0%, #FFC107 100%)', '⏳', 'white'),
                'RESOLU': ('linear-gradient(135deg, #4CAF50 0%, #8BC34A 100%)', '✅', 'white'),
                'IGNORE': ('linear-gradient(135deg, #9E9E9E 0%, #BDBDBD 100%)', '🚫', 'white'),
            }
            bg, icon, color = styles.get(obj.statut, ('#666', '?', 'white'))

            return format_html(
                '<span style="background: {}; color: {}; padding: 6px 12px; '
                'border-radius: 12px; font-size: 11px; font-weight: 600; '
                'box-shadow: 0 2px 4px rgba(0,0,0,0.15); display: inline-block;">'
                '{} {}</span>',
                bg, color, icon, obj.get_statut_display()
            )

        statut_badge.short_description = 'Statut'

        def epis_manquants_preview(self, obj):
            """Prévisualisation des EPIs manquants"""
            epis = obj.typeEpiManquants[:60]
            if len(obj.typeEpiManquants) > 60:
                epis += '...'

            return format_html(
                '<div style="max-width: 200px; font-size: 11px; color: #666;">'
                '<strong>🦺 EPI:</strong> {}'
                '</div>',
                epis
            )

        epis_manquants_preview.short_description = 'EPIs Manquants'

        def image_preview(self, obj):
            """Miniature de l'image"""
            if obj.image:
                return format_html(
                    '<img src="{}" width="60" height="60" '
                    'style="object-fit: cover; border-radius: 4px; '
                    'box-shadow: 0 2px 4px rgba(0,0,0,0.1);" />',
                    obj.image.url
                )
            return format_html('<span style="color: #999; font-size: 11px;">Pas d\'image</span>')

        image_preview.short_description = 'Image'

        def image_large(self, obj):
            """Image en grand pour la vue détaillée"""
            if obj.image:
                return format_html(
                    '<div style="text-align: center; padding: 20px; background: #f5f5f5; '
                    'border-radius: 8px;">'
                    '<img src="{}" style="max-width: 100%; height: auto; '
                    'border-radius: 8px; box-shadow: 0 4px 6px rgba(0,0,0,0.1);" />'
                    '</div>',
                    obj.image.url
                )
            return "Pas d'image disponible"

        image_large.short_description = 'Image complète'

        def created_at_display(self, obj):
            """Affichage formaté de la date"""
            return format_html(
                '<div style="font-size: 11px;">'
                '<div style="color: #333; font-weight: 500;">{}</div>'
                '<div style="color: #666;">{}</div>'
                '</div>',
                obj.created_at.strftime('%d/%m/%Y'),
                obj.created_at.strftime('%H:%M:%S')
            )

        created_at_display.short_description = 'Date création'

        def temps_ecoule(self, obj):
            """Temps écoulé depuis la création"""
            delta = timezone.now() - obj.created_at

            if delta.days == 0:
                if delta.seconds < 3600:
                    temps = f"{delta.seconds // 60} min"
                    color = '#f44336' if obj.statut == 'NOUVEAU' else '#666'
                else:
                    temps = f"{delta.seconds // 3600}h"
                    color = '#FF9800' if obj.statut == 'NOUVEAU' else '#666'
            elif delta.days == 1:
                temps = "Hier"
                color = '#FF9800'
            else:
                temps = f"{delta.days}j"
                color = '#757575'

            return format_html(
                '<span style="color: {}; font-weight: 600; font-size: 12px;">{}</span>',
                color, temps
            )

        temps_ecoule.short_description = 'Temps écoulé'

        def analyse_details(self, obj):
            """Détails d'analyse de l'alerte"""
            html = f'''
            <div style="background: white; padding: 20px; border-radius: 12px; 
                        box-shadow: 0 2px 8px rgba(0,0,0,0.1);">
                <h3 style="margin: 0 0 15px 0; font-size: 16px; font-weight: 600; color: #333;">
                    📊 Analyse de l'Alerte #{obj.id}
                </h3>

                <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 15px;">
                    <div style="background: #f5f5f5; padding: 15px; border-radius: 8px;">
                        <div style="font-size: 12px; color: #666; margin-bottom: 5px;">Employé</div>
                        <div style="font-size: 14px; font-weight: 600; color: #333;">
                            {obj.employee.name} {obj.employee.surname}
                        </div>
                        <div style="font-size: 11px; color: #666; margin-top: 3px;">
                            {obj.employee.poste} - {obj.employee.department}
                        </div>
                    </div>

                    <div style="background: #f5f5f5; padding: 15px; border-radius: 8px;">
                        <div style="font-size: 12px; color: #666; margin-bottom: 5px;">Modèle IA</div>
                        <div style="font-size: 14px; font-weight: 600; color: #333;">
                            {obj.modeleIA.name} (v{obj.modeleIA.version})
                        </div>
                        <div style="font-size: 11px; color: #666; margin-top: 3px;">
                            Sensibilité: {obj.modeleIA.sensibilite}%
                        </div>
                    </div>
                </div>

                <div style="margin-top: 15px; padding: 15px; background: #fff3e0; 
                            border-left: 4px solid #FF9800; border-radius: 4px;">
                    <div style="font-size: 12px; font-weight: 600; color: #F57C00; margin-bottom: 8px;">
                        🦺 EPIs Manquants
                    </div>
                    <div style="font-size: 13px; color: #666; line-height: 1.6;">
                        {obj.typeEpiManquants}
                    </div>
                </div>

                <div style="margin-top: 15px; display: flex; justify-content: space-between; 
                            font-size: 11px; color: #999;">
                    <span>Créée le: {obj.created_at.strftime('%d/%m/%Y à %H:%M:%S')}</span>
                    <span>ID: #{obj.id}</span>
                </div>
            </div>
            '''
            return mark_safe(html)

        analyse_details.short_description = 'Analyse détaillée'

        # Actions personnalisées
        def marquer_resolu(self, request, queryset):
            count = queryset.update(statut='RESOLU')
            self.message_user(request, f'{count} alerte(s) marquée(s) comme résolue(s).', messages.SUCCESS)

        marquer_resolu.short_description = "✅ Marquer comme résolu"

        def marquer_en_cours(self, request, queryset):
            count = queryset.update(statut='EN_COURS')
            self.message_user(request, f'{count} alerte(s) en cours de traitement.', messages.INFO)

        marquer_en_cours.short_description = "⏳ Marquer en cours"

        def marquer_ignore(self, request, queryset):
            count = queryset.update(statut='IGNORE')
            self.message_user(request, f'{count} alerte(s) ignorée(s).', messages.WARNING)

        marquer_ignore.short_description = "🚫 Ignorer"

        def changer_niveau_critique(self, request, queryset):
            count = queryset.update(niveau='CRITIQUE')
            self.message_user(request, f'{count} alerte(s) passée(s) en niveau CRITIQUE.', messages.ERROR)

        changer_niveau_critique.short_description = "🔴 Passer en CRITIQUE"

        def exporter_alertes_csv(self, request, queryset):
            response = HttpResponse(content_type='text/csv')
            response['Content-Disposition'] = 'attachment; filename="alertes_export.csv"'
            response.write('\ufeff')  # BOM pour Excel

            writer = csv.writer(response, delimiter=';')
            writer.writerow([
                'ID', 'Date', 'Employé', 'Poste', 'Département',
                'Niveau', 'Statut', 'EPIs Manquants', 'Modèle IA'
            ])

            for alerte in queryset:
                writer.writerow([
                    alerte.id,
                    alerte.created_at.strftime('%d/%m/%Y %H:%M'),
                    f"{alerte.employee.name} {alerte.employee.surname}",
                    alerte.employee.poste,
                    alerte.employee.department,
                    alerte.get_niveau_display(),
                    alerte.get_statut_display(),
                    alerte.typeEpiManquants,
                    f"{alerte.modeleIA.name} v{alerte.modeleIA.version}"
                ])

            self.message_user(request, f'Export CSV généré pour {queryset.count()} alerte(s).', messages.SUCCESS)
            return response

        exporter_alertes_csv.short_description = "📥 Exporter en CSV"
