from school.models import Term, Mark, TKMon
from school.templateExcel import  MAX_COL, CHECKED_DATE, normalize
from datetime import  datetime, timedelta

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
        a_subject.update({"isComment": subject.nx})

        arr_mark = m.toArrayMark(has_final=True)
        arr_time = m.toArrayTime()
        temp_mark = []
        for (i, a) in enumerate(arr_mark):
            if (a != '') & (i <= 3 * MAX_COL + 1):
                a_mark = {}
                a_mark.update({"n": i})
                a_mark.update({"m": normalize(a, subject.nx)})

                time_delta = timedelta(minutes=int(arr_time[i]))
                day = time_delta + CHECKED_DATE
                a_mark.update({"t": day.strftime("%y-%m-%d-%H-%M-%S")})
                temp_mark.append(a_mark)

        if selected_term.number == 2:
            term1 = Mark.objects.get(student_id=student_id, term_id=before_term, subject_id=subject)
            if term1.tb != None:
                a_mark = {}
                a_mark.update({"n": 3 * MAX_COL + 2})
                a_mark.update({"m": normalize(term1.tb, subject.nx)})

                term1_time = term1.toArrayTime()
                time_delta = timedelta(minutes=int(term1_time[3 * MAX_COL + 2]))
                day = time_delta + CHECKED_DATE
                a_mark.update({"t": day.strftime("%y-%m-%d-%H-%M-%S")})

                temp_mark.append(a_mark)
        if m.tb != None:
            a_mark = {}
            if selected_term.number == 1:
                a_mark.update({"n": 3 * MAX_COL + 2})
            else:
                a_mark.update({"n": 3 * MAX_COL + 3})
            a_mark.update({"m": normalize(m.tb, subject.nx)})

            time_delta = timedelta(minutes=int(arr_time[3 * MAX_COL + 2]))
            day = time_delta + CHECKED_DATE
            a_mark.update({"t": day.strftime("%y-%m-%d-%H-%M-%S")})
            temp_mark.append(a_mark)

        if selected_term.number == 2:
            tbnam = TKMon.objects.get(student_id=student_id, subject_id=subject)
            if tbnam.tb_nam != None:
                a_mark = {}
                a_mark.update({"n": 3 * MAX_COL + 4})
                a_mark.update({"m": normalize(tbnam.tb_nam, subject.nx)})

                # fix bug because forget save tbnam.time before, in viewmark.update_mark
                if tbnam.time == None:
                    tbnam.time = int(arr_time[3 * MAX_COL + 2])
                    tbnam.save()
                time_delta = timedelta(minutes=tbnam.time)

                day = time_delta + CHECKED_DATE
                a_mark.update({"t": day.strftime("%y-%m-%d-%H-%M-%S")})
                temp_mark.append(a_mark)

        a_subject.update({"mark": temp_mark})
        list.append(a_subject)
    return list