function(doc) {
  if (doc.type == 'record')
    emit([doc.created, doc._id, 0], doc);
  if (doc.type == 'task')
    emit([doc.created, doc.record_id, 1], doc);
}
