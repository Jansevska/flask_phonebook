const myModal = document.deleteContactModal('myModal')
const myInput = document.deleteContactModal('myInput')

myModal.deleteContactModal('shown.bs.modal', () => {
    myInput.focus()
})