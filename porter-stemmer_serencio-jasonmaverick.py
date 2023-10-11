from nltk.tokenize import word_tokenize
import csv
import pandas as pd
import sys
import re


class PorterStemmer:
    def isCons(self, letter):#function that returns true if a letter is a consonant otherwise false
        if letter == 'a' or letter == 'e' or letter == 'i' or letter == 'o' or letter == 'u':
            return False
        else:
            return True

    def isConsonant(self, word, i):#function that returns true only if the letter at i th position 
        #in the argument 'word' is a consonant.But if the letter is 'y' and the letter at i-1 th position 
        #is also a consonant, then it returns false.
        letter = word[i]
        if self.isCons(letter):
            if letter == 'y' and self.isCons(word[i-1]):
                return False
            else:
                return True
        else:
            return False

    def isVowel(self, word, i):#function that returns true if the letter at i th position in the argument 'word'
        #is a vowel
        return not(self.isConsonant(word, i))

    # *S
    def endsWith(self, stem, letter):#returns true if the word 'stem' ends with 'letter' 
        if stem.endswith(letter):
            return True
        else:
            return False

    # *v*
    def containsVowel(self, stem):#returns true if the word 'stem' contains a vowel
        for i in stem:
            if not self.isCons(i):
                return True
        return False

    # *d
    def doubleCons(self, stem):#returns true if the word 'stem' ends with 2 consonants
        if len(stem) >= 2:
            if self.isConsonant(stem, -1) and self.isConsonant(stem, -2):
                return True
            else:
                return False
        else:
            return False

    def getForm(self, word):
        #This function takes a word as an input, and checks for vowel and consonant sequences in that word.
        #vowel sequence is denoted by V and consonant sequences by C
        #For example, the word 'balloon' can be divived into following sequences:
        #'b' : C
        #'a' : V
        #'ll': C
        #'oo': V
        #'n' : C
        #So form = [C,V,C,V,C] and formstr = CVCVC
        form = []
        formStr = ''
        for i in range(len(word)):
            if self.isConsonant(word, i):
                if i != 0:
                    prev = form[-1]
                    if prev != 'C':
                        form.append('C')
                else:
                    form.append('C')
            else:
                if i != 0:
                    prev = form[-1]
                    if prev != 'V':
                        form.append('V')
                else:
                    form.append('V')
        for j in form:
            formStr += j
        return formStr

    def getM(self, word):
        #returns value of M which is equal to number of 'VC' in formstr
        #So in above example of word 'balloon', we have 2 'VC'

        form = self.getForm(word)
        m = form.count('VC')
        return m

    # *o
    def cvc(self, word):
        #returns true if the last 3 letters of the word are of the following pattern: consonant,vowel,consonant
        #but if the last word is either 'w','x' or 'y', it returns false
        if len(word) >= 3:
            f = -3
            s = -2
            t = -1
            third = word[t]
            if self.isConsonant(word, f) and self.isVowel(word, s) and self.isConsonant(word, t):
                if third != 'w' and third != 'x' and third != 'y':
                    return True
                else:
                    return False
            else:
                return False
        else:
            return False

    def replace(self, orig, rem, rep):
        #this function checks if string 'orig' ends with 'rem' and
        #replaces 'rem' by the substring 'rep'. The resulting string 'replaced'
        #is returned.

        result = orig.rfind(rem)
        base = orig[:result]
        replaced = base + rep
        return replaced

    def replaceM0(self, orig, rem, rep):
        #same as the function replace(), except that it checks the value of M for the 
        #base string. If it is >0 , it replaces 'rem' by 'rep', otherwise it returns the
        #original string

        result = orig.rfind(rem)
        base = orig[:result]
        if self.getM(base) > 0:
            replaced = base + rep
            return replaced
        else:
            return orig

    def replaceM1(self, orig, rem, rep):
        #same as replaceM0(), except that it replaces 'rem' by 'rep', only when M>1 for
        #the base string

        result = orig.rfind(rem)
        base = orig[:result]
        if self.getM(base) > 1:
            replaced = base + rep
            return replaced
        else:
            return orig

    def step1a(self, word):
        suffixes = [('sses', 'ss'), ('ies', 'i'), ('ss', 'ss'), ('s', ''),]

        for suffix, replacement in suffixes:
            if word.endswith(suffix):
                word = self.replace(word, suffix, replacement)

        return word


    def step1b(self, word):
        #this function checks if a word ends with 'eed','ed' or 'ing' and replces these substrings by
        #'ee','' and ''. If after the replacements in case of 'ed' and 'ing', the resulting word
        # -> ends with 'at','bl' or 'iz' : add 'e' to the end of the word
        # -> ends with 2 consonants and its last letter isn't 'l','s' or 'z': remove last letter of the word
        # -> has 1 as value of M and the cvc(word) returns true : add 'e' to the end of the word
        
        flag = False
        if word.endswith('eed'):
            result = word.rfind('eed')
            base = word[:result]
            if self.getM(base) > 0:
                word = base
                word += 'ee'
        elif word.endswith('ed'):
            result = word.rfind('ed')
            base = word[:result]
            if self.containsVowel(base):
                word = base
                flag = True
        elif word.endswith('ing'):
            result = word.rfind('ing')
            base = word[:result]
            if self.containsVowel(base):
                word = base
                flag = True
        if flag:
            if word.endswith('at') or word.endswith('bl') or word.endswith('iz'):
                word += 'e'
            elif self.doubleCons(word) and not self.endsWith(word, 'l') and not self.endsWith(word, 's') and not self.endsWith(word, 'z'): 
                word = word[:-1]
            elif self.getM(word) == 1 and self.cvc(word):
                word += 'e'
            else:
                pass
        else:
            pass
        return word

    def step1c(self, word):
        #In words ending with 'y' this function replaces 'y' by 'i'
        
        """step1c() turns terminal y to i when there is another vowel in the stem."""

        if word.endswith('y'):
            result = word.rfind('y')
            base = word[:result]
            if self.containsVowel(base):
                word = base
                word += 'i'
        return word
    
    def step2(self, word):
        suffixes = [('ational', 'ate'), ('tional', 'tion'), ('enci', 'ence'), ('anci', 'ance'), ('izer', 'ize'), ('abli', 'able'), ('alli', 'al'), ('entli', 'ent'), ('eli', 'e'), ('ousli', 'ous'), ('ization', 'ize'), ('ation', 'ate'), ('ator', 'ate'), ('alism', 'al'), ('iveness', 'ive'), ('fulness', 'ful'), ('ousness', 'ous'), ('aliti', 'al'), ('iviti', 'ive'), ('biliti', 'ble'),]

        for suffix, replacement in suffixes:
            if word.endswith(suffix):
                word = self.replaceM0(word, suffix, replacement)

        return word

    def step3(self, word):
        suffixes = [('icate', 'ic'), ('ative', ''), ('alize', 'al'), ('iciti', 'ic'), ('ful', ''),]

        for suffix, replacement in suffixes:
            if word.endswith(suffix):
                word = self.replaceM0(word, suffix, replacement)

        return word


    def step4(self, word):
        suffixes = ['al', 'ance', 'ence', 'er', 'ic', 'able', 'ible', 'ant',
        'ement', 'ment', 'ent', 'ou', 'ism', 'ate', 'iti', 'ous', 'ive', 'ize']

        for suffix in suffixes:
            if word.endswith(suffix):
                word = self.replaceM1(word, suffix, '')

        if word.endswith('ion'):
            result = word.rfind('ion')
            base = word[:result]
            if self.getM(base) > 1 and (self.endsWith(base, 's') or self.endsWith(base, 't')):
                word = base
            word = self.replaceM1(word, 'ion', '')

        return word


    def step5a(self, word):
        #this function checks if the word ends with 'e'. If it does, it checks the value of
        #M for the base word. If M>1, OR, If M = 1 and cvc(base) is false, it simply removes 'e'
        #ending.

        if word.endswith('e'):
            base = word[:-1]
            if self.getM(base) > 1:
                word = base
            elif self.getM(base) == 1 and not self.cvc(base):
                word = base
        return word

    def step5b(self, word):
        #this function checks if the value of M for the word is greater than 1 and it ends with 2 consonants
        # and it ends with 'l', it removes 'l'
        
        #step5b changes -ll to -l if m() > 1
        if self.getM(word) > 1 and self.doubleCons(word) and self.endsWith(word, 'l'):
            word = word[:-1]
        return word

    def stem(self, word):

        word = self.step1a(word)
        word = self.step1b(word)
        word = self.step1c(word)
        word = self.step2(word)
        word = self.step3(word)
        word = self.step4(word)
        word = self.step5a(word)
        word = self.step5b(word)
        return word
    
    # def replace_ere_with_er(self, stemmed_text):
    #     word = self.stem(stemmed_text)
    #     word = stemmed_text.split()  # Split the stemmed text into words
    #     for i in range(len(word)):
    #         if word[i].endswith("ere"):
    #             word[i] = word[i][:-1]  # Remove the "e" at the end
    #     return ' '.join(word)  # Join the modified words back into a sentence

# Initialize the class and methods/functions
stemmer = PorterStemmer()

def tokenize(text):
    words = re.findall(r'\b\w+\b', text)
    return words

def stem_text(text):
    words = tokenize(text)
    stemmed_words = [stemmer.stem(word) for word in words] #this is not using a built in function. The "stemmer" is the class and the "stem" is the last function/method
    return ' '.join(stemmed_words)

input = "4-cols_15k-rows.csv"
output = "stemmed_dataset_15k-rows_serencio-jasonmaverick.csv"

try:
    with open(input, 'r', encoding='utf-8') as input_file, open(output, 'w', newline='', encoding='utf-8') as output_file:
        csv_reader = csv.reader(input_file)
        csv_writer = csv.writer(output_file)

        for row in csv_reader:
            original_text = row[1]  # Assuming the text is in the second column
            stemmed_text = stem_text(original_text)
            row[1] = stemmed_text.lower()
            csv_writer.writerow(row)

    print(f"Stemmed data has been written to {output}")

except FileNotFoundError:
    print(f"File not found: {input}")
    sys.exit(1)

except UnicodeDecodeError:
    print(f"Unable to decode the file: {input}. Please make sure it is encoded in UTF-8.")
    sys.exit(1)

except Exception as e:
    print(f"An error occurred: {str(e)}")
    sys.exit(1)