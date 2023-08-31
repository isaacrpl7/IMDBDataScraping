def abbrev_to_integer(abbrev_string_number):
    count = abbrev_string_number.replace(u'\xa0', "").replace(" ","").strip("()")
    print(count)
    thousand = count.split("K")
    million = count.split("M")
    total_votes = 0
    if len(thousand) > 1:
        total_votes = int(float(thousand[0])*1000)
    elif len(million) > 1:
        total_votes = int(float(million[0])*1000000)
    else:
        total_votes = int(count)
    return total_votes