        $.getJSON((window.origin + "/api/v1/timesheets/" + ($("#username").text()).trim()), function (response) {
            var timesheets = response;

            var headerRow = "";
            var bodyRows = "";

            function format_it(time) {
                //ddd L
                return (moment(time).local().format('LTS')).toString();
            }

            function bring_it(date) {
                return (moment(date).local().format('L dddd')).toString();
            }

            headerRow += '<th scope="col">Time In:</th>\n';
            headerRow += '<th scope="col">Time Out:</th>\n';
            headerRow += '<th scope="col">Worked HRs:</th>\n';

            if (!($.isEmptyObject(timesheets))) {
               for (let ts of timesheets) {

                    if (bodyRows.includes(bring_it(ts.date))===false) {
                        // this if checks if the date is not already in bodyRows
                        bodyRows += '<tr>\n';
                        bodyRows += '<th scope="row" colspan="3">'+bring_it(ts.date)+'</th>\n';
                        bodyRows += '</tr>\n';
                    }
                    bodyRows += '<tr>\n';
                    bodyRows += '<td>' + format_it(ts.clock_in_time) + '</td>\n';
                    bodyRows += '<td>' + format_it(ts.clock_out_time) + '</td>\n';
                    bodyRows += '<td>' + '0.0 hours' + '</td>\n';
                    bodyRows += '</tr>\n';
                }
            }

             $("#timesheets_table").append('<table class="table table-bordered  table-dark table-sm table-hover table-striped">\n'+
            '<thead>\n<tr>' + headerRow +'</tr>\n</thead>\n'+
            '<tbody>\n' + bodyRows + '</tbody>\n</table>');
        });





