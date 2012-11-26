# -*- coding: utf-8 -*-
temp = u'a A à À ả Ả ã Ã á Á ạ Ạ ă Ă ằ Ằ ẳ Ẳ ẵ Ẵ ắ Ắ ặ Ặ â Â ầ Ầ ẩ Ẩ ẫ Ẫ ấ Ấ ậ Ậ b B c C d D đ Đ e E è È ẻ Ẻ ẽ Ẽ é É ẹ Ẹ ê Ê ề Ề ể Ể ễ Ễ ế Ế ệ Ệ g G h H i I ì Ì ỉ Ỉ ĩ Ĩ í Í ị Ị k K l L m M n N o O ò Ò ỏ Ỏ õ Õ ó Ó ọ Ọ ô Ô ồ Ồ ổ Ổ ỗ Ỗ ố Ố ộ Ộ ơ Ơ ờ Ờ ở Ở ỡ Ỡ ớ Ớ ợ Ợ p P q Q r R s S t T u U ù Ù ủ Ủ ũ Ũ ú Ú ụ Ụ ư Ư ừ Ừ ử Ử ữ Ữ ứ Ứ ự Ự v V x X y Y ỳ Ỳ ỷ Ỷ ỹ Ỹ ý Ý ỵ Ỵ' 

nosi = u'a A a A a A a A a A a A ă Ă ă Ă ă Ă ă Ă ă Ă ă Ă â Â â Â â Â â Â â Â â Â b B c C d D đ Đ e E e E e E e E e E e E ê Ê ê Ê ê Ê ê Ê ê Ê ê Ê g G h H i I i I i I i I i I i I k K l L m M n N o O o O o O o O o O o O ô Ô ô Ô ô Ô ô Ô ô Ô ô Ô ơ Ơ ơ Ơ ơ Ơ ơ Ơ ơ Ơ ơ Ơ p P q Q r R s S t T u U u U u U u U u U u U ư Ư ư Ư ư Ư ư Ư ư Ư ư Ư v V x X y Y y Y y Y y Y y Y y Y'

vnese_map = {}
for i in range(0, len(temp)):
    if temp[i] != ' ':
        if temp[i] in vnese_map:
            raise Exception('Yeah!ListsWrong') 
        else: 
            vnese_map[temp[i]] = (i, nosi[i])

def unicodecmp(left, right):
    minlen = min(len(left), len(right))
    for i in range(0, minlen):
        if not (left[i] in vnese_map and right[i] in vnese_map):
            buff = cmp(left[i], right[i])
            if buff: return buff
        else:
            if vnese_map[left[i]][0] < vnese_map[right[i]][0]:
                return -1
            elif vnese_map[left[i]][0] > vnese_map[right[i]][0]:
                return 1
    else:
        if len(left) < len(right): return -1
        elif len(left) > len(right): return 1
        else: return 0

def unsign(string):
    result = u''
    for i in range(0, len(string)):
        if string[i] in vnese_map:
            result += vnese_map[string[i]][1]
        else: result += string[i]
    return result

def invert(string):
    eles = string.split(' ')
    eles.reverse()
    return ' '.join([i if i else '' for i in eles])

def vncmp(left, right, col):
    if col == 'last_name':
        left = invert(left)
        right = invert(right)
    unsign_left = unsign(left)
    unsign_right = unsign(right)
    result = unicodecmp(unsign_left, unsign_right)
    if not result: return unicodecmp(left, right)
    else: return result

def multikeysort(items, columns, key=None, functions={}):
    #Sort a list of dictionary objects or objects by multiple keys bidirectionally.
    def getter(col):
        def wrapper(item):
            if col in ['family_name', 'middle_name',
                    'real_first_name', 'nick_name']:
                return getattr(item, col)()
            return getattr(item, col)
        return wrapper

    #Keyword Arguments:
    #items -- A list of dictionary objects or objects
    #columns -- A list of column names to sort by. Use -column to sort in
    #descending order
    #functions -- A Dictionary of Column Name -> Functions to normalize or
    #process each column value
    #getter -- Default "getter" if column function does not exist
    #          operator.itemgetter for Dictionaries
    #          operator.attrgetter for Objects
    comparers = []
    for col in columns:
        column = col[1:] if col.startswith('-') else col
        if not column in functions:
            functions[column] = (getter(column), col)
        comparers.append((functions[column], 1 if column == col else -1))

    def comparer(left, right):
        for func, polarity in comparers:
            result = vncmp(func[0](left), func[0](right), func[1])
            if result:
                return polarity * result
        else:
            return 0
    return sorted(items, cmp=comparer)

