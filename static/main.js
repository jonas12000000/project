document.addEventListener("DOMContentLoaded", function(){
    document.querySelector("#form1").onsubmit() = function(){
        const request = new XMLHttpRequest();
        const student_id = document.querySelector("#sid").value;
        const subject = document.querySelector('#subject').value;
        const exam_code = document.querySelector('#exam_code').value;
                                                  
        request.open('POST', '/result');
        request.onload = function(){
            const data = JSON.parse(request.responseText);
            
            if(data.success == false){
                var h3 = document.createElement('h3');
                
                h3.innerHTML = "Sorry, Can't find the result with provided input"
                document.querySelector('#result').appendChild(h3);
            }
            else{
                var table = document.createElement('table');
                
                table.setAttribute('class', 'table');
                
                var arrHead = new Array();
                arrHead = ['Name', 'Father name', 'Subject', 'Mark'];
                
                var arrValue = new Array();
                arrValue.push([data.name, data.father, data.subject, data.mark]);
                
                var tr = table.insertRow(-1);
                
                for (var h = 0; h < arrHead.length; h++) {
                var th = document.createElement('th');              // TABLE HEADER.
                th.innerHTML = arrHead[h];
                tr.appendChild(th);
                }
                
                for (var c = 0; c <= arrValue.length - 1; c++) {
                    tr = table.insertRow(-1);

                    for (var j = 0; j < arrHead.length; j++) {
                        var td = document.createElement('td');          // TABLE DEFINITION.
                        td = tr.insertCell(-1);
                        td.innerHTML = arrValue[c][j];                  // ADD VALUES TO EACH CELL.
                    }
                }
                document.querySelector('#result').appendChild(table);
            }
        }
        
        const data = new FormData();
        data.append('student_id', student_id);
        data.append('subject', subject);
        data.append('exam_code', exam_code);
    
        request.send(data);
        return false;
    }
});