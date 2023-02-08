import steps_ru
import steps_en
import steps_ukr
import steps_ital
import steps_fra
import steps_tur
import steps_ger
import steps_pol


def generate_steps(languages):
    result = {}
    for language in languages:
        for key, value in language.items():
            result[key] = result.get(key, []) + [value]
    return result


all_languages = generate_steps([steps_en.en, steps_ru.ru, steps_pol.pol, steps_ger.ger, steps_ukr.ukr, steps_fra.fra, steps_ital.ital, steps_tur.tur])

