var i = 2;
function addForm2() {
    let table = document.getElementById('RbSr_table');
    let newRow = table.insertRow();

    let newCell = newRow.insertCell();
    let num = document.createElement('td');
    num.setAttribute('id', 'num'+i);
    num.innerHTML = i;
    newCell.appendChild(num);
    i++ ;

    newCell = newRow.insertCell();
    let sr = document.createElement('input');
    sr.setAttribute('type', 'number');
    sr.setAttribute('name', 'Sr1');
    sr.setAttribute('step', '0.000001');
    sr.setAttribute('class', 'form-control');
    sr.setAttribute('max','1')
    sr.setAttribute('min','0')
    newCell.appendChild(sr);

    newCell = newRow.insertCell();
    let rb = document.createElement('input');
    rb.setAttribute('type', 'number');
    rb.setAttribute('name', 'Rb1');
    rb.setAttribute('step', '0.000001');
    rb.setAttribute('class', 'form-control');
    rb.setAttribute('max','1')
    rb.setAttribute('min','0')
    newCell.appendChild(rb);


    newCell = newRow.insertCell();
    let del = document.createElement('input');
    del.setAttribute('type', 'button');
    del.setAttribute('value', '削除');
    del.setAttribute('onclick', 'delform(this)');
    newCell.appendChild(del);
}

function delform(obj) {
    // 削除ボタンを押下された行を取得
    tr = obj.parentNode.parentNode;
    // trのインデックスを取得して行を削除する
    tr.parentNode.deleteRow(tr.sectionRowIndex);
}