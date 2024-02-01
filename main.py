import sys
from antlr4 import *

from MyNode import MyNode, Relation
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

	walker = ParseTreeWalker()

	myTree = MyRelationTree()

	listener = MyWalkListener(myTree, sparql_lexer)

	walker.walk(listener, start)

	if listener.error:
		sys.exit("could not parse the input")

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

	# myTree.print_tree_rev()

	sql_insert = lambda new_values, table: (" INSERT INTO " + table + " " \
												"VALUES " + ", ".join(new_values) + "; ") if len(new_values) > 0 else " "


	new_obj = myTree.search_for_new_objects()
	hierarchy = myTree.get_hierarchy()
	sqlrequest += sql_insert(hierarchy, "new_assumption")

	new_param = myTree.get_new_params(new_obj)
	new_params = myTree.get_new_param_ids(new_param, koncept_translation)
	sqlrequest += sql_insert(new_params, "new_param_id")

	new_values = myTree.get_values(new_param)
	sqlrequest += sql_insert(new_values, "new_values")

	if local:
		sqlrequest = sqlrequest.replace("'", "''")
	print(sqlrequest)
