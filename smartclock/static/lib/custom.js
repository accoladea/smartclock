function json2table(json) {
          var cols = Object.keys(json[0]);

          var headerRow = '';
          var bodyRows = '';

          function capitalizeFirstLetter(string) {
            return string.charAt(0).toUpperCase() + string.slice(1);
          }

          cols.map(function(col) {
            headerRow += '<th scope="col">' + capitalizeFirstLetter(col) + '</th>';
          });

          json.map(function(row) {
            bodyRows += '<tr>';

            cols.map(function(colName) {
              bodyRows += '<td>' + row[colName] + '</td>';
            })

          bodyRows += '</tr>';
          });

        return '<table class="table table-striped"><thead><tr>' +
                 headerRow +
                 '</tr></thead><tbody>' +
                 bodyRows +
                 '</tbody></table>';
  }


function list_timesheets(timesheets){
                var headerRow = "";
                var bodyRows = "";

                function format_it(time) {
                    return (moment(time).local().format('LLLL')).toString();
                }

                headerRow += '<th scope="col">Time In:</th>\n';
                headerRow += '<th scope="col">Time Out:</th>\n';
                headerRow += '<th scope="col">Worked HRs:</th>\n';

                if (!($.isEmptyObject(timesheets))) {
                   for (let timesheet of timesheets) {
                        bodyRows += '<tr>\n';
                        bodyRows += '<td>' + format_it(timesheet.clock_in_time) + '</td>\n';
                        bodyRows += '<td>' + format_it(timesheet.clock_out_time) + '</td>\n';
                        bodyRows += '<td>' + '0.0 hours' + '</td>\n';
                        bodyRows += '</tr>\n';
                    }
                }

                return '<table class="table table-striped">\n'+
                '<thead>\n<tr>' + headerRow +'</tr>\n</thead>\n'+
                '<tbody>\n' + bodyRows + '</tbody>\n</table>';

        }
