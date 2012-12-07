from school.models import Term, Mark, TKMon
from school.templateExcel import  MAX_COL, CHECKED_DATE, normalize

def getMarkForAStudent(student_id, term_id):
    selected_term = Term.objects.get(id=term_id)
    marks = Mark.objects.filter(term_id=term_id, student_id=student_id).order_by("subject_id__index",
        "subject_id__name")
    if selected_term.number == 2:
        before_term = Term.objects.get(year_id=selected_term.year_id, number=1)
        term1s = Mark.objects.filter(term_id=before_term, student_id=student_id).order_by("subject_id__index",
            "subject_id__name")
        tbnams = TKMon.objects.filter(student_id=student_id)

    list = []
    for m in marks:
        a_subject = {}
        subject = m.subject_id
        a_subject.update({"id": int(subject.id)})
        a_subject.update({"name": subject.name})
        arr_mark = m.toArrayMark()
        temp_mark = []
        for (i, a) in enumerate(arr_mark):
            if a != '':
                a_mark = {}
                a_mark.update({"n": i})
                a_mark.update({"m": normalize(a, subject.nx)})
                temp_mark.append(a_mark)
        if m.ck != None:
            a_mark = {}
            a_mark.update({"n": 3 * MAX_COL + 1})
            a_mark.update({"m": normalize(m.ck, subject.nx)})
            temp_mark.append(a_mark)
        if selected_term.number == 2:
            term1 = Mark.objects.get(student_id=student_id, term_id=before_term, subject_id=subject)
            if term1.tb != None:
                a_mark = {}
                a_mark.update({"n": 3 * MAX_COL + 2})
                a_mark.update({"m": normalize(term1.tb, subject.nx)})
                temp_mark.append(a_mark)
        if m.tb != None:
            a_mark = {}
            a_mark.update({"n": 3 * MAX_COL + 3})
            a_mark.update({"m": normalize(m.tb, subject.nx)})
            temp_mark.append(a_mark)
        if selected_term.number == 2:
            tbnam = TKMon.objects.get(student_id=student_id, subject_id=subject)
            a_mark = {}
            a_mark.update({"n": 3 * MAX_COL + 4})
            a_mark.update({"m": normalize(tbnam.tb_nam, subject.nx)})
            temp_mark.append(a_mark)

        a_subject.update({"mark": temp_mark})
        list.append(a_subject)
    return list