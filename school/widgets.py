from django import forms
            
class RadioFieldHorizontalRenderer(forms.RadioSelect.renderer):
    def render(self):
        return mark_safe(u'<ul>\n%s\n</ul>' % u'\n'.join([u'<p>%s</p>'
            % force_unicode(w) for w in self]))