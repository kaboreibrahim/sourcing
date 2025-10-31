import pandas as pd
from django.http import HttpResponse
from django.views.generic import View
from django.db.models import Q
from django.utils import timezone
from django.contrib.auth.mixins import LoginRequiredMixin
from ..models import Fournisseur
from openpyxl import Workbook
class FournisseurExportView(LoginRequiredMixin, View):
    """
    Vue pour exporter les fournisseurs au format Excel.
    """
    def get(self, request, *args, **kwargs):
        # Récupérer les paramètres de recherche
        search_params = {k: v for k, v in request.GET.items() if k != 'page' and v}
        
        # Construire la requête de base
        queryset = Fournisseur.objects.all().select_related('ville', 'ville__zone')
        
        # Appliquer les filtres
        if 'nom' in search_params:
            queryset = queryset.filter(nom__icontains=search_params['nom'])
            
        if 'nom_responsable' in search_params:
            queryset = queryset.filter(nom_responsable__icontains=search_params['nom_responsable'])
            
        if 'zone' in search_params:
            queryset = queryset.filter(ville__zone_id=search_params['zone'])
            
        if 'ville' in search_params:
            queryset = queryset.filter(ville_id=search_params['ville'])
            
        if 'commodite' in search_params:
            queryset = queryset.filter(commodites__id=search_params['commodite'])
            
        if 'has_gps' in search_params:
            if search_params['has_gps'] == 'yes':
                queryset = queryset.filter(latitude__isnull=False, longitude__isnull=False)
            elif search_params['has_gps'] == 'no':
                queryset = queryset.filter(Q(latitude__isnull=True) | Q(longitude__isnull=True))
                
        if 'has_doc' in search_params:
            if search_params['has_doc'] == 'yes':
                queryset = queryset.filter(document_fourni_aex=True)
            elif search_params['has_doc'] == 'no':
                queryset = queryset.filter(document_fourni_aex=False)
        
        # Préparer les données pour l'export
        data = []
        for fournisseur in queryset:
            data.append({
                'ID': str(fournisseur.id),
                'Nom': fournisseur.nom,
                'Nom responsable': fournisseur.nom_responsable,
                'Téléphone': fournisseur.contact or '',
                'localite': fournisseur.localite or '',
                'Ville': fournisseur.ville.nom if fournisseur.ville else '',
                'Zone': f"Zone {fournisseur.ville.zone.numero}" if (fournisseur.ville and fournisseur.ville.zone) else '',
                'Latitude': fournisseur.latitude or '',
                'Longitude': fournisseur.longitude or '',
                'Document AEX fourni': 'Oui' if fournisseur.document_fourni_aex else 'Non',
                'Date création': fournisseur.created_at.strftime('%d/%m/%Y %H:%M') if fournisseur.created_at else '',
                'Dernière modification': fournisseur.updated_at.strftime('%d/%m/%Y %H:%M') if fournisseur.updated_at else ''
            })
        
        # Créer un DataFrame pandas
        df = pd.DataFrame(data)
        
        # Créer la réponse HTTP avec le fichier Excel
        response = HttpResponse(
            content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
            headers={'Content-Disposition': f'attachment; filename="export_fournisseurs_{timezone.now().strftime("%Y%m%d_%H%M%S")}.xlsx"'},
        )
        
        # Écrire le DataFrame dans la réponse
        with pd.ExcelWriter(response, engine='openpyxl') as writer:
            df.to_excel(writer, index=False, sheet_name='Fournisseurs')
            
            # Ajuster la largeur des colonnes
            worksheet = writer.sheets['Fournisseurs']
            for idx, col in enumerate(df.columns):
                # Définir une largeur de colonne en fonction de la longueur du texte d'en-tête
                max_length = max(
                    df[col].astype(str).apply(len).max(),
                    len(str(col))
                ) + 2  # Petite marge
                worksheet.column_dimensions[chr(65 + idx)].width = min(max_length, 30)
        
        return response
