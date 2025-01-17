# -*- coding: utf-8 -*-
# Copyright (C) 2014 Universidade de Aveiro, DETI/IEETA, Bioinformatics Group - http://bioinformatics.ua.pt/
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
from questionnaire import *
from django.utils.translation import ugettext as _, ungettext
from django.utils.simplejson import dumps
from django.template.loader import render_to_string

import re

@question_proc('choice', 'choice-freeform')
def question_choice(request, question):
    choices = []
    jstriggers = []
    hasValue = False
    cd = question.getcheckdict()
    key = "question_%s" % question.number
    key2 = "question_%s_comment" % question.number
    val = None
    if key in request.POST:
        val = request.POST[key]
    else:
        if 'default' in cd:
            val = cd['default']

    if val != None and val != '' and "#" in val:
        val = val.split("#")[0]

    for choice in question.choices():
        choices.append( ( choice.value == val, choice, ) )
        hasValue = hasValue or choice.value == val

    #print "hasValue: "+str(hasValue)

    if question.type == 'choice-freeform':
        jstriggers.append('question_%s_comment' % question.number)

    return {
        'choices'   : choices,
        'sel_entry' : val == '_entry_',
        'qvalue'    : val or '',
        'required'  : True,
        'hasValue'  : hasValue,
        'comment'   : request.POST.get(key2, ""),
        'jstriggers': jstriggers,
    }

@answer_proc('choice', 'choice-freeform')
def process_choice(question, answer):
    required = question.getcheckdict().get('required', 0)

    opt = answer['ANSWER'] or ''
    if not opt and required:
        raise AnswerException(_(u'You must select an option'))
    if opt == '_entry_' and question.type == 'choice-freeform':
        opt = answer.get('comment','')
        if not opt:
            raise AnswerException(_(u'Field cannot be blank'))
        return dumps([[opt]])
    else:
        valid = [c.value for c in question.choices()]
        if opt not in valid and required:
            raise AnswerException(_(u'Invalid option!'))
    return dumps([opt])
add_type('choice', 'Choice [radio]')
add_type('choice-freeform', 'Choice with a freeform option [radio]')


@question_proc('choice-multiple', 'choice-multiple-freeform')
def question_multiple(request, question):
    key = "question_%s" % question.number
    #print key
    choices = []
    counter = 0
    cd = question.getcheckdict()
    val = ''
    hasValue = False
    try:
        val = request.POST.get(key, '')
    except:
        pass
    defaults = cd.get('default','').split(',')
    for choice in question.choices():
        counter += 1
        key = "question_%s_multiple_%d" % (question.number, choice.sortid)

        if key in request.POST or (val!=None and val != '' and (choice.value in val)) or \
          (request.method == 'GET' and choice.value in defaults):
            choices.append( (choice, key, ' checked',) )
            hasValue = hasValue or True
        else:
            choices.append( (choice, key, '',) )
    extracount = int(cd.get('extracount', 0))
    if not extracount and question.type == 'choice-multiple-freeform':
        extracount = 1
    extras = []

    for x in range(1, extracount+1):

        key = "question_%s_more%d" % (question.number, x)
        key_aux = "question_%s" % (question.number)

        if key_aux in request.POST :

            extras_value = request.POST[key_aux].split("||")
            if (len(extras_value)>1):
                extras.append( (key, extras_value[1]) )
                hasValue = hasValue or True
            else:
                extras.append( (key, '') )
        elif key in request.POST:
            extras.append( (key, request.POST[key]) )
            hasValue = hasValue or True
        else:
            extras.append( (key, '',) )

    return {
        "choices": choices,
        "extras": extras,
        "qvalue" : val,
        "hasValue": hasValue,
        "template"  : "questionnaire/choice-multiple-freeform.html",
        "required" : cd.get("required", False) and cd.get("required") != "0",

    }

@answer_proc('choice-multiple', 'choice-multiple-freeform')
def process_multiple(question, answer):
    multiple = []
    multiple_freeform = []

    requiredcount = 0
    required = question.getcheckdict().get('required', 0)
    if required:
        try:
            requiredcount = int(required)
        except ValueError:
            requiredcount = 1
    if requiredcount and requiredcount > question.choices().count():
        requiredcount = question.choices().count()


    import pdb
    #pdb.set_trace()
    for k, v in answer.items():
        #print "K: " + str(k)
        #print "V "
        if k.startswith('multiple'):
            multiple.append(v)
        if k.startswith('more') and len(v.strip()) > 0:
            multiple_freeform.append(v)

    if len(multiple) + len(multiple_freeform) < requiredcount:
        raise AnswerException(ungettext(u"You must select at least %d option",
                                        u"You must select at least %d options",
                                        requiredcount) % requiredcount)
    multiple.sort()
    if multiple_freeform:
        multiple.append(multiple_freeform)
    #print "Multiple" + str(multiple)
    return dumps(multiple)

def get_aux_text(full_value, choice_value, original_value=None):
    if (full_value==None):
        return original_value
    if isinstance(full_value, basestring):
        #print "full_value is string"
        _aux = full_value.split("#")
        #print _aux
        for v in _aux:
            if choice_value in v:
                values = re.findall(r'\{(.*?)\}', v)
                #print choice_value
                #print values
                if (len(values)>0):
                    return values[0]
        return ''
    else:
        return original_value



@question_proc('choice-multiple', 'choice-multiple-freeform-options')
def question_multiple_options(request, question):
    key = "question_%s" % question.number
    #print key
    hasValue = False
    choices = []
    counter = 0
    cd = question.getcheckdict()
    val = ''
    try:
        val = request.POST.get(key, '')
    except:
        pass
    defaults = cd.get('default','').split(',')

    for choice in question.choices():
        counter += 1

        key = "question_%s_multiple_%d" % (question.number, choice.sortid)
        key_value = "question_%s_%d_opt" % (question.number, choice.sortid)

        if val == None or val == '':
            try:
                val = request.POST.get(key, '')
            except:
                pass
        _aux = ""
        try:
            _aux = request.POST[key_value]
        except:
            pass

        def checkPartialIn(part, l):
            for elem in l:
                if part == elem.split('{')[0]:
                    return True

            return False

        if key in request.POST or (val!=None and checkPartialIn(choice.value,val.split('#'))) or \
          (request.method == 'GET' and choice.value in defaults):
            _tmp_v = get_aux_text(val,choice.value, _aux )
            if _tmp_v == None or _tmp_v == '':
                _tmp_v = _aux
            choices.append( (choice, key, ' checked',_tmp_v) )
            hasValue = hasValue or True

        else:
            _tmp_v = get_aux_text(val,choice.value, _aux )
            if _tmp_v == None or _tmp_v == '':
                _tmp_v = _aux
            choices.append( (choice, key, '',_tmp_v) )

    extracount = int(cd.get('extracount', 0))
    if not extracount and question.type == 'choice-multiple-freeform-options':
        extracount = 1
    extras = []
    #import pdb
    #pdb.set_trace()

    for x in range(1, extracount+1):

        key = "question_%s_more%d" % (question.number, x)
        key_aux = "question_%s" % (question.number)

        if key_aux in request.POST :

            extras_value = request.POST[key_aux].split("||")
            if (len(extras_value)>1):
                extras.append( (key, extras_value[1]) )

            else:
                extras.append( (key, '') )
        elif key in request.POST:
            extras.append( (key, request.POST[key]) )

        else:
            extras.append( (key, '',) )

    return {
        "choices": choices,
        "extras": extras,
        "qvalue" : val,
        "hasValue": hasValue,
        "template"  : "questionnaire/choice-multiple-freeform-options.html",
        "required" : cd.get("required", False) and cd.get("required") != "0",

    }

@answer_proc('choice-multiple', 'choice-multiple-freeform-options')
def process_multiple_options(question, answer):

    multiple = []
    multiple_freeform = []

    requiredcount = 0
    required = question.getcheckdict().get('required', 0)
    if required:
        try:
            requiredcount = int(required)
        except ValueError:
            requiredcount = 1
    if requiredcount and requiredcount > question.choices().count():
        requiredcount = question.choices().count()

    for k, v in answer.items():
        if k.startswith('multiple'):
            multiple.append(v)
        if k.startswith('more') and len(v.strip()) > 0:
            multiple_freeform.append(v)

    if len(multiple) + len(multiple_freeform) < requiredcount:
        raise AnswerException(ungettext(u"You must select at least %d option",
                                        u"You must select at least %d options",
                                        requiredcount) % requiredcount)
    multiple.sort()
    if multiple_freeform:
        multiple.append(multiple_freeform)

    return dumps(multiple)

def choice_list(value):
    choices = ['']
    try:
        choices = value.split('#')
    except:
        pass

    multiple_choices = {}

    for choice in choices[1:]:

        if '{' in choice and '}' in choice:
            values = choice.split('{')
            key = values[0]
            comment = values[1].replace('}', '')

            multiple_choices[key] = {'key': key, 'comment': comment}
        elif '||' in choice:
            values = choice.split('||')
            key = 'Other' #values[0]
            comment = values[1]

            multiple_choices[key] = {'key': key, 'comment': comment}
        else:
            multiple_choices[choice] = {'key': choice, 'comment': ''}

    return multiple_choices

def serialize_list(choice_list):
    tmp = ""

    for choice in choice_list:
        comment = choice['comment']

        tmp +="#%s" %(choice['key'])
        if comment != '':
            tmp += '{%s}' % (comment)




    return tmp


@show_summary('choice','choice-freeform','choice-multiple', 'choice-multiple-freeform', 'choice-multiple-freeform-options')
def show_summ(value):
    multiple_choices = choice_list(value).values()
    #return value
    return render_to_string('questionnaire/choice_summary.html', {'choices':multiple_choices})


@show_flat('choice','choice-freeform','choice-multiple', 'choice-multiple-freeform', 'choice-multiple-freeform-options')
def show_flat(question, value):

    multiple_choices = []
    ans_choices = choice_list(value)

    for choice in question.choices():
        if choice.text in ans_choices:
            comment = ans_choices[choice.text]['comment']

            multiple_choices.append(['Yes',''])
            multiple_choices.append([comment,''])
        else:
            multiple_choices.append(['', ''])
            multiple_choices.append(['', ''])

    return multiple_choices

add_type('choice-multiple', 'Multiple-Choice, Multiple-Answers [checkbox]')
add_type('choice-multiple-freeform', 'Multiple-Choice, Multiple-Answers, plus freeform [checkbox, input]')
add_type('choice-multiple-freeform-options', 'Multiple-Choice with Options, Multiple-Answers, plus freeform [checkbox, input]')


