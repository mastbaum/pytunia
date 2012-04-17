function(doc) {
  if (doc.type == 'record')
    emit([doc._id, 0, null], doc);
  if (doc.type == 'task') {
    if (doc.kwargs && doc.kwargs.testname)
      emit([doc.record_id, 1, doc.kwargs.testname], doc);
    else
      emit([doc.record_id, 1, doc.name], doc);
  }
}
