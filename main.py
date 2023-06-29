import sys
from antlr4 import *

from MyNode import MyNode
from MyRelationTree import MyRelationTree
from MyWalkListener import MyWalkListener
from gen.SparqlLexer import SparqlLexer
from gen.SparqlParser import SparqlParser

# https://github.com/antlr/grammars-v4/blob/master/sparql/Sparql.g4
# attention: grammar now changed a little

if __name__ == '__main__':

	sqlrequest = ""
	if len(sys.argv) < 2:
		local = True
		with open('query_new.txt', 'r') as fr:
			query = fr.read()
	else:
		local = False
		query = sys.argv[1]

	sparql_lexer = SparqlLexer(InputStream(query))
	sparql_tokens = CommonTokenStream(sparql_lexer)
	sparql_parser = SparqlParser(sparql_tokens)
	start = sparql_parser.query()

	# walker = ParseTreeWalker()
	for i in range(len(sparql_tokens.tokens)):
		print(sparql_tokens.get(i).text + " type: " + str(sparql_tokens.get(i).type) + ": " + " + " + str(sparql_tokens.get(i)))


	walker = ParseTreeWalker()
	print(sparql_lexer)
	print(sparql_tokens)
	print(sparql_parser)
	print(start)

	myTree = MyRelationTree()

	listener = MyWalkListener(myTree)

	walker.walk(listener, start)

	if listener.error:
		sys.exit("could not parse the input")

	A_NODE = MyNode('verb', 'a', False)
	HAT_WERT_NODE = MyNode('konzept', 'hat_Wert', False)
	HAT_PARAMETER_NODE = MyNode('konzept', 'hat_Parameter', False)
	HAT_NAME_NODE = MyNode('konzept', 'hat_Name', False)
	CORRESPONDS_NODE = MyNode('konzept', 'korrespondiert_mit', False)

	koncept_translation = {
		'Frequenz': 'Frequenz',
		'Aktivierungsleistung': 'Aktivierungsleistung',
		'Aktivierungszeit': 'Aktivierungszeit',
		'Biegesteifigkeit': 'Biegesteifigkeit',
		'Blockierkraft': 'Blockierkraft',
		'Einzeldrahtwiderstand': 'Einzeldrahtwiderstand',
		'elektrische_Kapazitaet': 'elektrische_Kapazitaet',
		'elektrischer_Widerstand': 'elektrischer_Widerstand',
		# 'freie_Dehnung': 'freie_Dehnung',
		'freie_Streckung': 'freie_Streckung',
		'freier_Hub': 'freier_Hub',
		'mechanische_Bewegung': 'mechanische_Bewegung',
		'neutrale_Faserlage': 'neutrale_Faserlage',
		'piezoelektrisches_Moment': 'piezoelektrische_Moment',
		'Dichte': 'Dichte',
		'elektrisches_Flaechenverhaeltnis': 'elektrisches_Flaechenverhaeltnis',
		'Emissionsgrad': 'Emissionsgrad',
		'Aktuationsquerschnitt': 'Aktuationsquerschnitt',
		'Ausgangsbreite': 'Ausgangsbreite',
		'Ausgangsdicke': 'Ausgangsdicke',
		'Ausgangselektrodendicke': 'Ausgangselektrodendicke',
		'Ausgangslaenge': 'Ausgangslaenge',
		'Ausgangsdrahtlaenge': 'Ausgangsdrahtlaenge',
		'Ausgangsquerschnitt': 'Ausgangsquerschnitt',
		'Ausgangswandlerhoehe': 'Ausgangswandlerhoehe',
		'Breite': 'Breite',
		'Dicke': 'Dicke',
		'Drahtdurchmesser': 'Drahtdurchmesser',
		'Ausgangsdrahtdurchmesser': 'Ausgangsdrahtdurchmesser',
		# 'Ausgangsdrahtlaenge': 'Ausgangsdrahtlaenge',
		# 'Ausgangsquerschnitt': 'Ausgangsquerschnitt',
		'Flaeche': 'Flaeche',
		'Hoehe': 'Hoehe',
		'Laenge': 'Laenge',
		'lineare_Abmessung': 'lineare_Abmessung',
		'Oberflaeche': 'Oberflaeche',
		'Schichtanzahl': 'Schichtanzahl',
		'Wandlerhoehe': 'Wandlerhoehe',
		'Halteleistung': 'Halteleistung',
		'Masse': 'Masse',
		'Ader-Abhaengigkeitsparameter': 'Ader-Abhaengigkeitsparameter',
		'Anisotropie': 'Anisotropie',
		'Anisotropiefeld': 'Anisotropiefeld',
		'Curie_Temperatur': 'Curie_Temperatur',
		'Dehnung_Uebergang_1': 'Dehnung_Uebergang_1',
		'Dehnung_Uebergang_2': 'Dehnung_Uebergang_2',
		'maximale_Dehnung': 'maximale_Dehnung',
		'maximale_Dehnung_im_Magnetfeld': 'maximale_Dehnung_im_Magnetfeld',
		'Maximale_Phasentransformationsdehnung': 'Maximale_Phasentransformationsdehnung',
		'Plateau-Start-Dehnung': 'Anfangsdehnung_fuer_quasi-plastische_Verformung', # Dehnung_Uebergang_1?
		'Plateau-Finish-Dehnung': 'Enddehnung_fuer_quasi-plastische_Verformung', # Dehnung_Uebergang_2?
		'Durchbruchfeldstaerke': 'Durchbruchfeldstaerke',
		'E-Modul_fuer_Austenit': 'E-Modul_fuer_Austenit',
		'E-Modul_fuer_Austenit_elastisch': 'E-Modul_fuer_Austenit_elastisch',
		'E-Modul_fuer_Austenit_pseudoplastisch': 'E-Modul_fuer_Austenit_pseudoplastisch',
		'E-Modul_fuer_Martensit': 'E-Modul_fuer_Martensit',
		'E-Modul_fuer_Martensit_elastisch': 'E-Modul_fuer_Martensit_elastisch', # Modul_fuer_Martensit
		'E-Modul_fuer_Martensit_pseudoplastisch': 'E-Modul_fuer_Martensit_pseudoplastisch',
		'Elastizitaetsmodul': 'Elastizitaetsmodul',
		'Elastizitaetsmodul_nach_Neo_Hookean': 'Elastizitaetsmodul_nach_Neo_Hookean',
		'Elastizitaetsmodul_nach_Yeoh_1': 'Elastizitaetsmodul_nach_Yeoh_1',
		'Elastizitaetsmodul_nach_Yeoh_2': 'Elastizitaetsmodul_nach_Yeoh_2',
		'Elastizitaetsmodul_nach_Yeoh_3': 'Elastizitaetsmodul_nach_Yeoh_3',
		'elektrische_Permittivitaet_bei_konstanter_mechanischer_Dehnung': 'C10',
		'elektrische_Permittivitaet_bei_konstanter_mechanischer_Spannung': 'C00',
		'inverse_elektrische_Permittivitaet_bei_konstanter_mechanischer_Dehnung': 'C11',
		'inverse_elektrische_Permittivitaet_bei_konstanter_mechanischer_Spannung': 'C01',
		'Gitterkonstante_a': 'Gitterkonstante_a',
		'Gitterkonstante_b': 'Gitterkonstante_b',
		'Gitterkonstante_c': 'Gitterkonstante_c',
		'Kristallstruktur': 'Kristallstruktur',
		'magnetische_Anisotropiekonstante': 'magnetische_Anisotropiekonstante',
		'Martensitgehalt': 'Martensitgehalt',
		'maximale_Blockierspannung': 'maximale_Blockierspannung',
		'maximale_Blockierspannung_entlastet': 'maximale_Blockierspannung_entlastet',
		'maximale_Blockierspannung_belastet': 'maximale_Blockierspannung_belastet',
		'maximale_Einsatztemperatur': 'maximale_Einsatztemperatur',
		'maximale_Spannung': 'maximale_Spannung',
		'mechanische_Nachgiebigkeit_bei_konstantem_elektrischen_Feld': 'A00',
		'mechanische_Nachgiebigkeit_bei_konstanter_elektrischer_Flussdichte': 'A01',
		'Austenit-Finish-Spannung_bei_pseudoelastischer_Verformung': 'Austenit-Finish-Spannung_bei_pseudoelastischer_Verformung',
		'Austenit-Start-Spannung_bei_pseudoelastischer_Verformung': 'Austenit-Start-Spannung_bei_pseudoelastischer_Verformung',
		'Martensit-Finish-Spannung_bei_pseudoelastischer_Verformung': 'Martensit-Finish-Spannung_bei_pseudoelastischer_Verformung',
		'Martensit-Start-Spannung_bei_pseudoelastischer_Verformung': 'Martensit-Start-Spannung_bei_pseudoelastischer_Verformung',
		'maximal_magnetische_Spannung': 'maximale_magnetische_Spannung',
		'Plateau-Finish-Spannung': 'Endspannung_fuer_quasi-plastische_Verformung',
		'Plateau-Start-Spannung': 'Anfangsspannung_fuer_quasi-plastische_Verformung',
		'Spannung_Uebergang_1': 'Spannung_Uebergang_1', # Plateau-Start-Spannung
		'Spannung_Uebergang_2': 'Spannung_Uebergang_2', # Plateau-Finish-Spannung
		'mechanische_Steifigkeit_bei_konstantem_elektrischem_Feld': 'A10',
		'mechanische_Steifigkeit_bei_konstanter_elektrischer_Flussdichte': 'A11',
		'relative_Permeabilitaet': 'relative_Permeabilitaet',
		'Austenit_Finish_Temperatur': 'Austenit_Finish_Temperatur',
		'Austenit_Start_Temperatur': 'Austenit_Start_Temperatur',
		'Martensit_Finish_Temperatur': 'Martensit_Finish_Temperatur',
		'Martensit_Start_Temperatur': 'Martensit_Start_Temperatur',
		'piezoelektrische_Dehnungskonstante': 'B10',
		'piezoelektrische_Ladungskonstante': 'B00',
		'piezoelektrische_Spannungskonstante': 'B01',
		'Poissonzahl': 'Poissonzahl',
		'relative_Permittivitaet': 'relative_Permittivitaet',
		'Saettigungspolarisation': 'Saettigungspolarisation',
		'schwere_Achse': 'schwere_Achse',
		'spezifischer_elektrischer_Widerstand': 'spezifischer_elektrischer_Widerstand',
		'spezifischer_elektrischer_Widerstand_Durchschnitt': 'spezifischer_elektrischer_Widerstand_Durchschnitt',
		'spezifischer_elektrischer_Widerstand_T1': 'spezifischer_elektrischer_Widerstand_T1',
		'spezifischer_elektrischer_Widerstand_T2': 'spezifischer_elektrischer_Widerstand_T2',
		'spezifischer_Widerstand_fuer_Austenit': 'spezifischer_Widerstand_fuer_Austenit',
		'spezifischer_Widerstand_fuer_Martensit': 'spezifischer_Widerstand_fuer_Martensit',
		'Temperatur-Skalierungsparameter': 'Temperatur-Skalierungsparameter',
		'Temperaturgradient_fuer_Austenit': 'Temperaturgradient_fuer_Austenit',
		'Temperaturgradient_fuer_Martensit': 'Temperaturgradient_fuer_Martensit',
		'Transformationsenthalpie': 'Transformationsenthalpie',
		'Transformationstemperatur': 'Transformationstemperatur',
		'Waermekapazitaet': 'Waermekapazitaet',
		'Waermeleitfaehigkeit': 'Waermeleitfaehigkeit',
		'Waermeuebergangskoeffizient': 'Waermeuebergangskoeffizient',
		'Zwillingsspannung': 'Zwillingsspannung',
		# 'Ausgangsdicke': 'Ausgangsdicke',
		'Permeabilitaet_im_Vakuum': 'Permeabilitaet_im_Vakuum',
		'Permitivitaet_im_Vakuum': 'Permitivitaet_im_Vakuum',
		'Volumenausdehnungskoeffizient_fuer_Austenit': 'Volumenausdehnungskoeffizient_Austenit',
		'Volumenausdehnungskoeffizient_Martensit': 'Volumenausdehnungskoeffizient_fuer_Martensit',
		'Umgebungstemperatur': 'Umgebungstemperatur',
		'Referenztemperatur': 'Referenztemperatur',
		'Dehnung': 'Dehnung',
		'Dehnung_Everett': 'Dehnung_Everett',
		'Dehnung_FORC': 'Dehnung_FORC',
		'elektrische_Feldstaerke': 'elektrische_Feldstaerke',
		'elektrische_Flussdichte': 'elektrische_Flussdichte',
		'elektrische_Spannung': 'elektrische_Spannung',
		'Betriebsspannung': 'Betriebsspannung',
		'Multilayer-Lagenspannung': 'Multilayer-Lagenspannung',
		'elektrostatischer_Druck': 'elektrostatischer_Druck',
		'Hub': 'Hub',
		'Aktuationskraft': 'Aktuationskraft',
		'Kraft': 'Kraft',
		'magnetische_Feldenergiedichte': 'magnetische_Feldenergiedichte',
		'magnetische_Feldstaerke': 'magnetische_Feldstaerke',
		'magnetische_Flussdichte': 'magnetische_Flussdichte',
		'magnetische_Polarisierung': 'magnetische_Polarisierung',
		'magnetische_Spannung_alpha': 'magnetische_Spannung_alpha',
		'magnetische_Spannung_beta': 'magnetische_Spannung_beta',
		'Magnetisierung': 'Magnetisierung',
		'phasenspezifischer_Widerstandstemperaturkoeffizient_A': 'phas_Wider_Temp_Koeff_A',
		'phasenspezifischer_Widerstandstemperaturkoeffizient_M': 'phas_Wider_Temp_Koeff_M',
		'magnetische_Spannung': 'magnetische_Spannung',
		'mechanische_Spannung': 'mechanische_Spannung',
		'Streckung': 'Streckung',
		'Temperatur': 'Temperatur',
		'Temperaturabh_spez_elektr_Widerstand': 'temp_abh_spez_el_Widerstand',
		'thermischer_Einfluss': 'thermischer_Einfluss',
		'Parameter': 'undefined'
	}

	myTree.traverseVars()

	sql_insert_new_material = lambda materials: "INSERT INTO new_mat_samples " \
													"SELECT DISTINCT new_mat.mat " \
													"FROM (VALUES " + materials + ") AS new_mat (mat) " \
														"LEFT OUTER JOIN  " \
														"(	SELECT sample_id AS name " \
															"FROM sample " \
															"UNION SELECT mat_name AS name FROM material " \
															"UNION SELECT concr_component_name AS name FROM concr_component " \
														") m " \
															"ON m.name = new_mat.mat " \
														"WHERE m.name IS NULL ; "

	sql_insert_param_id = lambda new_params: "INSERT INTO new_param_id " +\
												"SELECT DISTINCT " +\
												"newval.new_val_id, " +\
												"p.param_id " +\
												"FROM  " +\
													"(VALUES " + new_params + ") AS newval (new_val_id, param_id) " +\
													"LEFT OUTER JOIN " +\
													"param p " +\
													"ON p.param_id = newval.param_id " +\
												"WHERE p.param_id IS NOT NULL"

	sql_insert_value = lambda new_values: "INSERT INTO new_value " +\
												"SELECT DISTINCT " +\
												"valid.new_val_id, " +\
												"newval.value " +\
												"FROM  " +\
													"(VALUES " + new_values + ") AS newval (new_val_id, value) " +\
													"LEFT OUTER JOIN " +\
													"new_param_id valid " +\
													"ON valid.new_val_id = newval.new_val_id " +\
												"WHERE valid.new_val_id IS NOT NULL"

	sql_insert_material = lambda new_material: "INSERT INTO new_mat_sample_id " +\
												"SELECT DISTINCT " +\
												"valid.new_val_id, " +\
												"m.mat_sample_id " +\
												"FROM " +\
													"(SELECT DISTINCT newmat.new_val_id, COALESCE(nam.mat_sample_id, newmat.material) AS material FROM (VALUES " + new_material + ") AS newmat (new_val_id, material) " +\
													"LEFT JOIN ( " +\
														"SELECT sample_id AS mat_sample_id, " +\
														"sample_name AS name " +\
														"FROM sample " +\
														"UNION SELECT mat_id AS mat_sample_id, " +\
														"mat_name AS name " +\
														"FROM material " +\
														"UNION SELECT concr_component.concr_component_id AS mat_sample_id, " +\
														"concr_component.concr_component_name AS name " +\
														"FROM concr_component " +\
														") nam " +\
														"ON newmat.material = nam.name " +\
													") init " +\
													"LEFT OUTER JOIN  " \
													"(SELECT sample_id AS mat_sample_id FROM sample " \
														"UNION SELECT mat_id AS mat_sample_id FROM material " \
														"UNION SELECT mat_sample_id AS mat_sample_id FROM new_mat_samples " \
														"UNION SELECT concr_component_id AS mat_sample_id FROM concr_component " \
													") m " \
													"ON m.mat_sample_id = init.material " +\
													"LEFT OUTER JOIN " +\
														"new_param_id valid " +\
													"ON valid.new_val_id = init.new_val_id " +\
												"WHERE m.mat_sample_id IS NOT NULL AND valid.new_val_id IS NOT NULL"

	# Todo: add only correspondance if they correscpnd: if the are the same material.
	sql_insert_correspondings = lambda new_corres: "INSERT INTO new_corresponds " +\
												"SELECT DISTINCT " +\
												"valid.new_val_id, " +\
												"valid2.new_val_id " +\
												"FROM  " +\
													"(VALUES " + new_corres + ") AS newcor (first, sec) " +\
													"LEFT OUTER JOIN " +\
													"new_param_id valid " +\
													"ON valid.new_val_id = newcor.first " +\
													"LEFT OUTER JOIN " +\
													"new_param_id valid2 " +\
													"ON valid2.new_val_id = newcor.sec " +\
												"WHERE valid.new_val_id IS NOT NULL AND valid2.new_val_id IS NOT NULL"

	new_mat = myTree.get_new_materials()

	# Todo : better way, maybe with lamda function
	if len(new_mat)>0:
		materials = "('" + "'), ('".join(new_mat) + "')"
		sqlrequest += sql_insert_new_material(materials)

	new_values = myTree.get_new_params(koncept_translation)

	tree = myTree.forward
	rev_tree = myTree.reverse
	params = []
	values = []
	material = []
	for new_value in new_values:
		if tree.get(new_value) is not None:
			if tree[new_value].get(A_NODE) is not None:
				for obj in tree[new_value][A_NODE]:
					if obj.type == 'string':
						params.append("('" + new_value.name + "', '" + obj.name + "')")
					if obj.type == 'konzept':
						if koncept_translation.get(obj.name) is not None:
							params.append("('" + new_value.name + "', '" + koncept_translation[obj.name] + "')")
						else:
							params.append("('" + new_value.name + "', '" + obj.name + "')")

			if tree[new_value].get(HAT_WERT_NODE) is not None:
				for obj in tree[new_value][HAT_WERT_NODE]:
					if obj.type == 'numeric':
						values.append("('" + new_value.name + "', " + obj.name + ")")

		if rev_tree.get(new_value) is not None:
			if rev_tree[new_value].get(HAT_PARAMETER_NODE) is not None:
				for subrev in rev_tree[new_value][HAT_PARAMETER_NODE]:
					if tree.get(subrev) is not None:
						if tree[subrev].get(HAT_NAME_NODE) is not None:
							for obj2 in tree[subrev][HAT_NAME_NODE]:
								if obj2.type == 'string' or obj2.type == 'konzept':
									material.append("('" + new_value.name + "', '" + obj2.name + "')")
	corres = myTree.search_for_correspondings()
	correspon = []
	for co in corres:
		if tree.get(co) is not None:
			if tree[co].get(CORRESPONDS_NODE) is not None:
				for co2 in tree[co][CORRESPONDS_NODE]:
					correspon.append("('" + co.name + "', '" + co2.name + "')")


	if len(params)>0:
		sqlrequest += sql_insert_param_id(", ".join(params)) + " ; "
	if len(values) > 0:
		sqlrequest += sql_insert_value(", ".join(values)) + " ; "
	if len(material) > 0:
		sqlrequest += sql_insert_material(", ".join(material)) + " ; "
	if len(correspon) > 0:
		sqlrequest += sql_insert_correspondings(", ".join(correspon)) + " ; "

	if local:
		sqlrequest = sqlrequest.replace("'", "''")
	print(sqlrequest)
