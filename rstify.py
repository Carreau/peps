from textwrap import indent, wrap

indent_level = lambda line: len(line) - len(line.lstrip())

import re
enumre = re.compile('\d+\. ')

def fix_word_emphase(word):
    if '*' in word:
        print('yep word:', word)
        return '``%s``'% word
    return word

def fix_line_emphasis(line):
    if '*'in line:
        return ' '.join([ fix_word_emphase(word) for word in line.split(' ')])
    return line



def getparagraph(line, iterator):
    text = line.strip()
    for line in iterator:
        if line.strip():
            text = text + ' ' + line.strip()
        else:
            return fix_line_emphasis(text)
    return fix_line_emphasis(text)
    
def rstify(_pep):
    pep = iter(_pep)
    for line in pep:
        if 'text/x-rst' in line:
            yield line
            yield from pep
            return
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
            yield "\n* "+'\n  '.join(wrap(getparagraph(line.strip()[2:], pep)+'\n',77))+'\n'

        if enumre.match(line.strip()):
            num = line.strip()[:1]
            yield "\n%s. "% num+'\n   '.join(wrap(getparagraph(line.strip()[2:], pep)+'\n',76))+'\n'


        elif line.startswith(' '):
            indentlevel = indent_level(line)-4
            gp = getparagraph(line, pep)
            par = '\n'.join(wrap(gp+'\n', 79-indentlevel))+'\n'
            if indentlevel == 0:
                yield '\n'+par
            else:
                yield '\n::\n\n'+indent(par, ' '*indentlevel)
        elif line =='\n':
            yield line
        elif line == '\x0c\n':
            yield '..\n'
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
    print('writing to ', out)
    with open(out,'w') as f:
        text = ''.join([r for r in rstify(pep)])
        lines = [line for line in text.splitlines()]
        f.write('\n'.join(lines))

        
if __name__ == '__main__':
    import sys
    for file in sys.argv[1:]:
        process_file(file)
    
