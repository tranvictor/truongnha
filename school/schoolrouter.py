class SchoolRouter(object):
	def allow_syncdb(self, db, model):
		if db == 'default':
			return model._meta.app_label != 'school'
		else:
			if model._meta.app_label == 'school':
				return True
			else:
				return False
		return None

