/**
 * Show functions to be exported from the design doc.
 */

// summary view with basic record information and "percent awesome" bar data
exports.summary = {
    map: function(doc) {
        if (doc.type == 'record')
            emit([doc._id, 1], doc);
        if (doc.type == 'task')
            emit([doc.record_id, 0], doc);
    }
};

// get tasks for a given record
// returns record row followed by associated tasks
exports.tasks_by_record = {
    map: function(doc) {
    if (doc.type == 'record')
        emit([doc._id, null, 0], doc);
    if (doc.type == 'task')
        if (doc.kwargs && doc.kwargs.testname)
            emit([doc.record_id, doc.kwargs.testname, 1], doc);
        else
            emit([doc.record_id, doc.name, 1], doc);
    }
};

// get a given task for all records
exports.tasks_by_name = {
    map: function(doc) {
        if (doc.type == 'task') {
            // rattests are special
            if (doc.kwargs && doc.kwargs.testname)
                emit([doc.kwargs.testname, doc.created], doc);
            else
                emit([doc.name, doc.created], doc);
        }
    }
};

exports.slaves_by_hostname = {
    map: function(doc) {
        if(doc.type == 'slave')
            emit(doc.fqdn, doc);
    }
};

