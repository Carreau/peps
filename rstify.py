from textwrap import indent, wrap

from  more_itertools import peekable


WRAPL_LENGHT = 70

indent_level = lambda line: len(line) - len(line.lstrip())

import re
enumre = re.compile('\d+\. ')

def fix_word_emphase(word):
    if '*' in word:
        if word.startswith('*') and word.endswith('*'):
            # plain text *word* is bold, change to `**word**`
            print('making', word, 'bold')
            return '*%s*'% word
        print('making', word, 'inline pre')
        return '``%s``'% word
    return word

def fix_line_emphasis(line):
    if '*'in line:
        return ' '.join([ fix_word_emphase(word) for word in line.split(' ')])
    return line



def getparagraph(line, iterator):
    text = line.strip()
    n = ''
    try:
        n = iterator.peek().strip()
    except StopIteration:
        print('peeked on ', line)
        return line
    if enumre.match(n) or n.startswith('-'):
        return text
    for line in iterator:
        if line.strip():
            text = text + ' ' + line.strip()
        else:
            return fix_line_emphasis(text)
    return fix_line_emphasis(text)

class NothingToDo(Exception):pass
    
def rstify(_pep):
    pep = peekable(iter(_pep))
    for line in pep:
        if 'text/x-rst' in line:
            raise NothingToDo('this pep is already RST')
            #yield line
            #yield from pep
            #return
        if 'Content-Type' in line:
            continue
        if 'Created' in line :
            # insert content-type before created.
            yield 'Content-Type: text/x-rst\n'
        if line == '\n':
            yield '\n'
            break
        else:
            yield line

    for line in pep:

        if line.strip().startswith('-'):
            yield "\n* "+'\n  '.join(wrap(getparagraph(line.strip()[2:], pep)+'\n',
                WRAPL_LENGHT-3))+'\n'

        elif enumre.match(line.strip()):
            num = line.strip()[:1]
            yield "\n%s. "% num+'\n   '.join(wrap(getparagraph(line.strip()[2:], pep)+'\n',WRAPL_LENGHT-3))+'\n'
        elif line.strip().startswith('['):
            # references:
            yield '\n.. '+line.strip()+'\n'


        elif line.startswith(' '):
            indentlevel = indent_level(line)-4
            gp = getparagraph(line, pep)
            par = '\n'.join(wrap(gp+'\n', WRAPL_LENGHT-indentlevel))+'\n'
            if indentlevel == 0:
                yield '\n'+par
            else:
                yield '\n::\n\n'+indent(par, ' '*indentlevel)
        elif line =='\n':
            yield line
        elif line == '\x0c\n':
            yield '\n..\n'
            break
        else:
            yield '\n'
            yield line
            yield '='*len(line.strip('\n'))

    for line in pep:
        yield ' '*3+line
            

    
def process_file(file):
    
    with open(file) as f:
        pep = f.readlines()
    out= '%s%s'%(file[:-3], 'rst' )
    text = ''.join([r for r in rstify(pep)])
    lines = [line for line in text.splitlines()]
    with open(out,'w') as f:
        f.write('\n'.join(lines))
        print('writing to ', out)

        
if __name__ == '__main__':
    import sys
    for file in sys.argv[1:]:
        try:
            process_file(file)
        except NothingToDo:
            pass
    
