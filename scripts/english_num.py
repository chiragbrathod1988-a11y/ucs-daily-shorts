"""Spoken English numbers the way Indian traders say them, written in Devanagari so the Hindi
voice pronounces them naturally (Hinglish).  e.g. 22852 -> "ट्वेंटी टू थाउज़ेंड एट हंड्रेड फिफ्टी टू"
(= "twenty two thousand eight hundred fifty two"), 23047 -> "ट्वेंटी थ्री थाउज़ेंड फोर्टी सेवन".
"""
ONES = ["ज़ीरो", "वन", "टू", "थ्री", "फोर", "फाइव", "सिक्स", "सेवन", "एट", "नाइन", "टेन",
        "इलेवन", "ट्वेल्व", "थर्टीन", "फोर्टीन", "फिफ्टीन", "सिक्सटीन", "सेवनटीन", "एटीन", "नाइनटीन"]
TENS = {2: "ट्वेंटी", 3: "थर्टी", 4: "फोर्टी", 5: "फिफ्टी", 6: "सिक्सटी", 7: "सेवेंटी", 8: "एटी", 9: "नाइंटी"}

def two(n: int) -> str:
    if n < 20:
        return ONES[n]
    t, o = divmod(n, 10)
    return TENS[t] + ("" if o == 0 else " " + ONES[o])

def words(n) -> str:
    n = int(round(n))
    if n < 0:
        return "माइनस " + words(-n)
    if n < 100:
        return two(n)
    if n < 1000:                       # 238 -> "two hundred thirty eight" (full form is clearest in the voice)
        h, r = divmod(n, 100)
        return ONES[h] + " हंड्रेड" + ("" if r == 0 else " " + two(r))
    th, r = divmod(n, 1000)
    out = two(th) + " थाउज़ेंड" if th < 100 else words(th) + " थाउज़ेंड"
    if r == 0:
        return out
    if r < 100:                        # 23047 -> "twenty three thousand forty seven"
        return out + " " + two(r)
    h, rr = divmod(r, 100)             # 22852 -> "... thousand eight hundred fifty two"
    return out + " " + ONES[h] + " हंड्रेड" + ("" if rr == 0 else " " + two(rr))

if __name__ == "__main__":
    for x in (22852, 23047, 23157, 22742, 22547, 22894, 22937, 238, 30, 22605, 23000):
        print(x, words(x))


# Latin-script version for the Microsoft neural voice, which reads English words in Latin script most clearly.
_O = ["zero", "one", "two", "three", "four", "five", "six", "seven", "eight", "nine", "ten", "eleven", "twelve",
      "thirteen", "fourteen", "fifteen", "sixteen", "seventeen", "eighteen", "nineteen"]
_T = {2: "twenty", 3: "thirty", 4: "forty", 5: "fifty", 6: "sixty", 7: "seventy", 8: "eighty", 9: "ninety"}

def _two(n):
    if n < 20:
        return _O[n]
    t, o = divmod(n, 10)
    return _T[t] + ("" if o == 0 else " " + _O[o])

def latin(n) -> str:
    n = int(round(n))
    if n < 0:
        return "minus " + latin(-n)
    if n < 100:
        return _two(n)
    if n < 1000:
        h, r = divmod(n, 100)
        return _O[h] + " hundred" + ("" if r == 0 else " " + _two(r))
    th, r = divmod(n, 1000)
    out = (_two(th) if th < 100 else latin(th)) + " thousand"
    if r == 0:
        return out
    if r < 100:
        return out + " " + _two(r)
    h, rr = divmod(r, 100)
    return out + " " + _O[h] + " hundred" + ("" if rr == 0 else " " + _two(rr))

# Latin-script version (for the ElevenLabs voice, which reads English words in Latin script most naturally)
L_ONES = ["zero", "one", "two", "three", "four", "five", "six", "seven", "eight", "nine", "ten", "eleven", "twelve",
          "thirteen", "fourteen", "fifteen", "sixteen", "seventeen", "eighteen", "nineteen"]
L_TENS = {2: "twenty", 3: "thirty", 4: "forty", 5: "fifty", 6: "sixty", 7: "seventy", 8: "eighty", 9: "ninety"}

def _l2(n):
    if n < 20: return L_ONES[n]
    t, o = divmod(n, 10)
    return L_TENS[t] + ("" if o == 0 else " " + L_ONES[o])

def words_latin(n) -> str:
    n = int(round(float(n)))
    if n < 0: return "minus " + words_latin(-n)
    if n < 100: return _l2(n)
    if n < 1000:
        h, r = divmod(n, 100)
        return L_ONES[h] + " hundred" + ("" if r == 0 else " " + _l2(r))
    th, r = divmod(n, 1000)
    out = (_l2(th) if th < 100 else words_latin(th)) + " thousand"
    if r == 0: return out
    if r < 100: return out + " " + _l2(r)
    h, rr = divmod(r, 100)
    return out + " " + L_ONES[h] + " hundred" + ("" if rr == 0 else " " + _l2(rr))
