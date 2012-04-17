function(doc) {
  if (doc.type == 'task') {
    if (doc.kwargs && doc.kwargs.testname)
      emit([doc.kwargs.testname, doc.created], doc)
    else
      emit([doc.name, doc.created], doc);
  }
}
