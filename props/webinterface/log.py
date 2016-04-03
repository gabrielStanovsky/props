def log(fname,request,sent):
   try:
      ip = request.environ.get('REMOTE_ADDR')
      fh=file(fname,"a")
      fh.write("%s\n%s\n====\n" % (ip,sent.encode("utf8")))
      fh.close()
   except: 
      pass
