from utils.data_handler import FileHandler
from utils.key_phrase_extractor import Extractor


def calculate_costs():
    file_handler = FileHandler()
    reg_ref1, reg_corpus1, reg_ref2, reg_corpus2 = file_handler.get_reg_texts_cols()

    kp_extractor = Extractor()

    # extract key phrases from corpus 1 and find matching documents in corpus 2.
    filtered_ref_corpus1, filtered_ref_corpus2, non_matched_refs = kp_extractor.get_matching_records(reg_corpus1,
                                                                                                     reg_corpus2,
                                                                                                     reg_ref1,
                                                                                                     reg_ref2,
                                                                                                     log=False)

    prod_calc = (len(filtered_ref_corpus1) * len(filtered_ref_corpus2))
    cost = 0.0015 * prod_calc
    time = (1.5 * prod_calc)/60
    return cost, time


print(f"\nThe estimated cost for doing this analysis is: ${calculate_costs()[0]}\n")
print(f"The estimated (rough if all requests get processed as expected) time to run is {calculate_costs()[1]} minutes")
