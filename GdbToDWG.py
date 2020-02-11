# -*- coding: utf-8 -*-
# Name: GdbToDWG.py
# Description: Export vers un beau DWG
# Author: mav

# To Do : remplacer la gdb temporaire par in_memory

# Import system modules
import arcpy, os, datetime
# from arcpy import env

# Début du minutage, hors import des modules
now = datetime.datetime.now() 

# Définition des variables globales
# Chemins d'accès
input_gdb_folder = r"D:\99_Tmp\1_Operations\Laburets"
input_gdb = "Topo_Travail.gdb"
input_gdb_path = os.path.join(input_gdb_folder, input_gdb)
output_gdb_folder = r"D:\99_Tmp"
output_gdb = "TmpToDWG.gdb"
output_gdb_path = os.path.join(output_gdb_folder, output_gdb)
gabarit_dao_path = r"D:\90_Param\ArcGIS\Scripts\Gdb2Cad\Export_200_CC47.dwg"
output_dao = "OperationArcheo.dwg"
output_dao_path = os.path.join(input_gdb_folder, output_dao)


# CE à exporter vers le DWG
ceAExporter = [u'CFSd_Pgn', u'CFSd_Pln', u'CpRp_Pln', u'Emprise_Pgn', u'FUS_Bord_Pln', u'FUS_Pgn', u'FUS_Pln', u'Topo_Pgn', u'Topo_Pln', u'Topo_Pts', u'Topo_Stations']
# CE avec un champ 'ACTIF' à utiliser pour filtrer
ceAFiltrer = [u'CFSd_Pgn', u'CFSd_Pln', u'Emprise_Pgn', u'FUS_Pgn', u'FUS_Pln', u'Topo_Pgn', u'Topo_Pln']

# Création de la géodatabase fichier temporaire
if arcpy.Exists(output_gdb_path):
	print u"Suppression de la précédente géodatabase temporaire..."
	arcpy.Delete_management(output_gdb_path)
	print u"Géodatabase temporaire précédente supprimée."
print u"Création de la géodatabase temporaire..."
arcpy.CreateFileGDB_management (output_gdb_folder, output_gdb)
print u"Géodatabase temporaire créée !\n"

# Définition de la Gdb du chantier comme espace de travail par défaut
# Cela permet d'énumérer les CE facilement.
arcpy.env.workspace = input_gdb_path
# Création de la liste des classes d'entités en entrée
fcList = arcpy.ListFeatureClasses()

# On parcourt la gdb à la recherche des CE conventionnelles. 
# Leur absence ne cause ainsi pas d'erreur.
for fc in fcList:
	if fc in ceAExporter:
		output_fc = os.path.join(output_gdb_path, fc)
		print u'Copie de ' + fc + '...'
		arcpy.Copy_management(fc, output_fc)
		print fc + u' a été copié.'
print u"Tout a été copié !\n"
del fc, fcList

# Définition de la Gdb temporaire comme espace de travail par défaut
# On pourrait peut-être utiliser à la place ceAExporter... 
# -> vérifier si erreur en cas d'absence d'une CE
arcpy.env.workspace = output_gdb_path
fcList = arcpy.ListFeatureClasses()

# Ajout des champs DAO
print u"Ajout et calcul des champs DAO aux classes d'entités..."

for fc in fcList:
	print u'Traitement de ' + fc + '...'
	arcpy.AddField_management(fc, "Layer", "TEXT")
	# Pour les points topo, traitement spécifique 
	if fc in ["Topo_Pts","Topo_Stations"]:
		arcpy.AddField_management(fc, "CadType", "TEXT")
		arcpy.AddField_management(fc, "RefName", "TEXT")
		# Permet l'insertion des points en tant que bloc "point topo"
		arcpy.CalculateField_management(fc, "CadType", "'INSERT'", "PYTHON_9.3")
		# On définit l'attribut "ALT" des bloc AutoCAD TopoPoint et TopoStation
		arcpy.AlterField_management(fc, "Z", "ALT")
		if fc == "Topo_Pts":
			# On nomme ici le bloc "point topo" inséré dans le gabarit DAO 		
			arcpy.CalculateField_management(fc, "RefName", "'TopoPoint'", "PYTHON_9.3")
			# On définit les attributs du bloc "point topo", ici MAT, ALT et COD
			arcpy.AlterField_management(fc, "PT_ID", "MAT")
			arcpy.AlterField_management(fc, "ATT1", "COD")
			arcpy.CalculateField_management(fc, "Layer", "'Point topo - ' + !CODE_DESCR!", "PYTHON_9.3")
		else: # fc=="Topo_Stations"
			# On nomme ici le bloc "station" inséré dans le gabarit DAO 		
			arcpy.CalculateField_management(fc, "RefName", "'TopoStation'", "PYTHON_9.3")
			# On définit les attributs du bloc "station topo", ici MAT et COD
			arcpy.AlterField_management(fc, "Matricule", "MAT")
			arcpy.AlterField_management(fc, "Observation", "COD")
			arcpy.CalculateField_management(fc, "Layer", "'Station topo'", "PYTHON_9.3")	
	elif fc == "FUS_Bord_Pln":
		arcpy.CalculateField_management(fc, "Layer", "!LEGENDE!", "PYTHON_9.3")
	else:
		arcpy.CalculateField_management(fc, "Layer", "!CODE_DESCR!", "PYTHON_9.3")
	print u"Attributs DAO pour " + fc + u" ajoutés."

print u"Champs DAO ajoutés aux classes d'entités et calculés.\n"

# Export DXF/DWG
# Attention c'est le gabarit qui définit le format de fichier (DWG/DXF,version)
# mais sans modifier l'extension
print u"Génération du fihier DAO..."
arcpy.ExportCAD_conversion(fcList, "DWG_R2007", output_dao_path,"Ignore_Filenames_in_Tables","Append_To_Existing_Files", gabarit_dao_path)

later = datetime.datetime.now() 
elapsed = later - now  
print(u'Le fichier DAO a été généré en  {} secondes.').format(elapsed)


# except Exception as err:
    # arcpy.AddError(err)
    # print err