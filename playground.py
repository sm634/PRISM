from utils.key_phrase_extractor import Extractor

ref2 = ["'EBA-OA 4(6.37)"]
text2 = ["""Outsourcing should not lower the suitability requirements applied to the members of an institution’s 
management body, directors and persons responsible for the management of the payment institution and key 
function holders. Institutions and payment institutions should have adequate competence and sufficient and appropriately 
skilled resources to ensure appropriate management and oversight of outsourcing arrangements."""]

ref1 = ["ICTRM 5.4"]
text1 = ["""Members of the management body of the financial entity shall actively keep up to date with sufficient 
knowledge and skills to understand and assess ICT risk and its impact on the operations of the financial entity, 
including by following specific training on a regular basis, commensurate to the ICT risk being managed."""]


kp_extractor = Extractor()

filtered_ref_corpus1, filtered_ref_corpus2, non_matching_ref = kp_extractor.get_matching_records(text1, text2, ref1, ref2)

filtered_corpus1 = [doc for doc in filtered_ref_corpus1.values()]
filtered_corpus2 = [doc for doc in filtered_ref_corpus2.values()]
filtered_ref1 = [ref for ref in filtered_ref_corpus1.keys()]
filtered_ref2 = [ref for ref in filtered_ref_corpus2.keys()]

breakpoint()

