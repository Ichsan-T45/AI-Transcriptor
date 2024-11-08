$(document).ready(function() {
    $('#add-phrase').click(function() {
        // Ambil nilai dari input
        const value = $('#phrase-input').val();
        
        // Cek apakah input tidak kosong
        if(value) {
            // Tambahkan item baru ke dalam daftar
            const newItem = `<li><small> ${value} </small><i class="remove-item fa-solid fa-eraser ms-2" style="color: #c1152f;"></i></li>`
            $('#phrase-list').append(newItem);
            
            // Tambahkan item ke input
            $('#phrase-list').val($('#phrase-list').val() +";"+value )
            // Kosongkan input setelah menambah item
            $('#item-input').val = "";
        } else {
            alert('Masukkan item terlebih dahulu!');
        }

        // Event delegation untuk tombol hapus
        $('#phrase-list').on('click', '.remove-item', function() {
            // Hapus elemen <li> yang mengandung tombol "Hapus" yang diklik
            $(this).parent().remove();
        });
    });
});