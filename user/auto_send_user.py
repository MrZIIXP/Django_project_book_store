def user_check(request):
   rq = request.session
   is_has_user = True if 'user' in rq else False
   context = {
		'has_user': is_has_user
	}
   if is_has_user:
      context['user'] = rq['user']
   return context