document.getElementById('emailForm').addEventListener('submit', function(event) {
    event.preventDefault();  // Mencegah form submit biasa

    const senderEmail = document.getElementById('sender');
    const receiverEmail = document.getElementById('receiver');
    const password = document.getElementById('password');
    const statusList = document.getElementById('statusList');
    const senderError = document.getElementById('senderError');
    const receiverError = document.getElementById('receiverError');
    const passwordError = document.getElementById('passwordError');
    const ccInputs = document.querySelectorAll('input[name="cc[]"]');  // Menangkap semua input email CC
    let valid = true;

    // Cek format email pengirim
    const emailPattern = /^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,6}$/;

    // Validasi email pengirim
    if (!emailPattern.test(senderEmail.value)) {
        senderError.style.display = 'block';
        valid = false;
    } else {
        senderError.style.display = 'none';
    }

    // Validasi email penerima
    if (!emailPattern.test(receiverEmail.value)) {
        receiverError.style.display = 'block';
        valid = false;
    } else {
        receiverError.style.display = 'none';
    }

    // Validasi app password (16 karakter alfanumerik dengan spasi yang boleh diinput tapi dihapus)
    const passwordWithoutSpaces = password.value.replace(/\s+/g, '');  // Menghapus semua spasi
    const passwordPattern = /^[a-zA-Z0-9]{16}$/;  // Regex untuk 16 karakter alfanumerik tanpa spasi
    
    if (!passwordPattern.test(passwordWithoutSpaces)) {
        passwordError.style.display = 'block';
        valid = false;
    } else {
        passwordError.style.display = 'none';
    }

    // Validasi email CC (Hanya jika ada input CC)
    ccInputs.forEach(function(ccInput) {
        if (ccInput.value.trim() !== "") {  // Hanya validasi jika ada email CC yang diisi
            const ccError = document.createElement('div');
            ccError.classList.add('text-danger');
            
            if (!emailPattern.test(ccInput.value)) {
                ccError.textContent = 'Format email CC tidak valid.';
                ccInput.parentElement.appendChild(ccError);
                valid = false;
            } else {
                // Menghapus pesan error jika email valid
                if (ccInput.parentElement.contains(ccError)) {
                    ccInput.parentElement.removeChild(ccError);
                }
            }
        }
    });

    // Jika ada input yang tidak valid, hentikan form submit
    if (!valid) {
        return;
    }

    // Jika validasi sukses, kirim data ke server menggunakan Fetch API
    const formData = new FormData(this);  // Ambil data form

    fetch('/', {
        method: 'POST',
        body: formData,
    })
    .then(response => response.json())
    .then(data => {
        // Menampilkan status pengiriman email
        statusList.innerHTML = '';  // Bersihkan daftar status sebelumnya
        data.status.forEach(statusMessage => {
            const statusItem = document.createElement('li');
            statusItem.classList.add('list-group-item');
            statusItem.textContent = statusMessage;
            statusList.appendChild(statusItem);
        });
    })
    .catch(error => {
        console.error('Terjadi kesalahan:', error);
    });
});

// Fitur untuk menambah input CC
document.getElementById('addCCButton').addEventListener('click', function() {
    const ccContainer = document.getElementById('ccContainer');
    const newInputGroup = document.createElement('div');
    newInputGroup.classList.add('input-group', 'mb-2');
    
    const newInput = document.createElement('input');
    newInput.type = 'email';
    newInput.name = 'cc[]';
    newInput.classList.add('form-control');
    newInput.placeholder = 'Email CC';
    
    const removeButton = document.createElement('button');
    removeButton.type = 'button';
    removeButton.classList.add('btn', 'btn-outline-danger');
    removeButton.textContent = 'X';
    
    removeButton.addEventListener('click', function() {
        newInputGroup.remove();
    });
    
    newInputGroup.appendChild(newInput);
    newInputGroup.appendChild(removeButton);
    
    ccContainer.appendChild(newInputGroup);
});
