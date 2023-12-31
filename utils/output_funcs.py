
def model_judgment_criteria(similarity_score):
    try:
        similarity_score = float(similarity_score)
        if similarity_score >= 0.7:
            return 'Aligned'
        elif 0.5 <= similarity_score < 0.7:
            return 'Partial'
        elif similarity_score < 0.5:
            return 'Unlikely'
    except TypeError:
        return 'None'
