#from srComparator.screenshots.Comparator import Comparator
import src.screenshots.comparison.Comparator as Comparator

chrome_2 = 'images/chrome_2.png'
chrome = "images/chrome.png"
firefox = "images/firefox.png"
pdiff = "images/diff.png"
pdiff_inv = "images/diff_invert.png"

#c = Comparator()
#Comparator.size_difference(chrome, firefox)
Comparator.__match_sizes(chrome, firefox)
#Comparator.diff(chrome, firefox)
assert(Comparator.size_difference(chrome, firefox) == 287334)

assert(Comparator.difference_percentage(chrome, chrome) == 0.0)
assert(Comparator.difference_percentage(firefox, firefox) == 0.0)

assert(int(Comparator.difference_percentage(chrome, firefox)) == 21)
assert(int(Comparator.difference_percentage(firefox, chrome)) == 21)

assert(Comparator.difference_percentage(chrome, chrome_2) == 0.0)
assert(Comparator.difference_percentage(chrome_2, chrome) == 0.0)

assert(int(Comparator.difference_percentage(firefox, chrome_2)) == 21)
assert(int(Comparator.difference_percentage(chrome_2, firefox)) == 21)

assert(Comparator.difference_percentage(pdiff, pdiff_inv) == 100.0)
assert(Comparator.difference_percentage(pdiff_inv, pdiff) == 100.0)
assert(Comparator.difference_percentage(pdiff_inv, pdiff_inv) == 0.0)
assert(Comparator.difference_percentage(pdiff, pdiff) == 0.0)

Comparator.highlight_differences(firefox, chrome)