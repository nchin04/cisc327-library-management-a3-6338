import pytest
from unittest.mock import Mock
from services.library_service import pay_late_fees, refund_late_fee_payment
from services.payment_service import PaymentGateway


#required tests
def test_pay_late_fees_success(mocker):
    mocker.patch("services.library_service.get_book_by_id", return_value={"id": 1, "title": "Kevin Durant"})
    mocker.patch("services.library_service.calculate_late_fee_for_book", return_value={"fee_amount": 7.50})

    mock_gateway = Mock(spec=PaymentGateway)
    mock_gateway.process_payment.return_value = (True, "txn_121", "Success")

    success, msg, txn = pay_late_fees("127456", 1, mock_gateway)

    assert success is True
    assert "payment successful" in msg.lower()
    assert txn =="txn_121"
    mock_gateway.process_payment.assert_called_once_with(
        patron_id= "127456",
        amount=7.50,
        description="Late fees for 'Kevin Durant'"
    )


def test_pay_late_fees_declined(mocker):
    mocker.patch("services.library_service.get_book_by_id", return_value={"id": 2, "title": "SGA"})
    mocker.patch("services.library_service.calculate_late_fee_for_book", return_value={"fee_amount": 12.00})

    mock_gateway = Mock(spec=PaymentGateway)
    mock_gateway.process_payment.return_value =(False,"txn_322","Declined")

    success, msg, txn = pay_late_fees("123457", 2, mock_gateway)

    assert success is False
    assert "declined" in msg.lower()
    mock_gateway.process_payment.assert_called_once_with(
        patron_id= "123457",
        amount=12.00,
        description="Late fees for 'SGA'"
    )


def test_pay_late_fees_invalid_patron_id(mocker):
    mocker.patch("services.library_service.get_book_by_id", return_value={"id": 3, "title": "Lebron James"})
    mocker.patch("services.library_service.calculate_late_fee_for_book", return_value={"fee_amount": 6.00})

    mock_gateway = Mock(spec=PaymentGateway)

    success,msg, txn =pay_late_fees("b^&3*", 3, mock_gateway)

    assert success is False
    assert "invalid patron id" in msg.lower()
    mock_gateway.process_payment.assert_not_called()


def test_pay_late_fees_zero_late_fees(mocker):
    mocker.patch("services.library_service.get_book_by_id", return_value={"id": 4, "title": "Ant"})
    mocker.patch("services.library_service.calculate_late_fee_for_book", return_value={"fee_amount": 0.0})

    mock_gateway = Mock(spec=PaymentGateway)

    success, msg, txn = pay_late_fees("222256",4, mock_gateway)
    assert success is False
    assert "no late fees" in msg.lower()
    mock_gateway.process_payment.assert_not_called()


def test_pay_late_fees_network_error(mocker):
    mocker.patch("services.library_service.get_book_by_id", return_value={"id": 5, "title": "Luka"})
    mocker.patch("services.library_service.calculate_late_fee_for_book", return_value={"fee_amount": 5.00})

    mock_gateway = Mock(spec=PaymentGateway)
    mock_gateway.process_payment.side_effect = RuntimeError("Network down" )

    success, msg, txn = pay_late_fees("444449", 5, mock_gateway)
    assert success is False
    assert "network" in msg.lower()
    mock_gateway.process_payment.assert_called_once_with(
        patron_id= "444449",
        amount= 5.00,
        description="Late fees for 'Luka'"
    )

def test_refund_late_fee_payment_success(mocker):
    mock_gateway = Mock(spec=PaymentGateway)
    mock_gateway.refund_payment.return_value = (True,"Success")
    success, msg = refund_late_fee_payment("txn_003", 2.00, mock_gateway)

    assert success is True
    assert "success" in msg.lower()
    mock_gateway.refund_payment.assert_called_once_with("txn_003",2.00)


def test_refund_late_fee_payment_invalid_transaction_id(mocker):
    mock_gateway = Mock(spec=PaymentGateway)
    success, msg = refund_late_fee_payment("_txn", 15.00, mock_gateway)
    assert success is False
    assert "invalid" in msg.lower()
    mock_gateway.refund_payment.assert_not_called()


def test_refund_late_fee_payment_invalid_amounts(mocker):
    mock_gateway = Mock(spec=PaymentGateway)
    success1, msg1 =refund_late_fee_payment("txn_387", -4.00,mock_gateway)  
    success2, msg2 =refund_late_fee_payment("txn_905", 0.00, mock_gateway)  
    success3, msg3 =refund_late_fee_payment("txn_420",60.0, mock_gateway)  
    assert success1 is False and ("invalid" in msg1.lower() or "amount" in msg1.lower())
    assert success2 is False and ("invalid" in msg2.lower() or "amount" in msg2.lower())
    assert success3 is False and ("exceeds"  in msg3.lower() or "amount" in msg3.lower())
    mock_gateway.refund_payment.assert_not_called()


#Statement and branch coverage

def test_process_payment():
    gateway = PaymentGateway()

    success,txn_id, msg = gateway.process_payment("490496", -20, "Late fees")
    assert success is False
    assert "greater than 0" in msg.lower()

    success,txn_id, msg = gateway.process_payment("490490", 2000, "Late fees")
    assert success is False
    assert "exceeds limit" in msg.lower()

    success,txn_id, msg = gateway.process_payment("11122", 15, "Late fees")
    assert success is False
    assert "invalid patron" in msg.lower()



def test_refund_payment():
    gateway = PaymentGateway()

    success,msg = gateway.refund_payment("not_txn", 5)
    assert success is False
    assert "invalid transaction" in msg.lower()

    success,msg = gateway.refund_payment("txn_237",-90)
    assert success is False
    assert "invalid refund amount" in msg.lower()

    success,msg = gateway.refund_payment("txn_888",5)
    assert success is True
    assert "refund of $5.00 processed successfully" in msg.lower()


def test_verify_payment_status():
    gateway = PaymentGateway()

    result = gateway.verify_payment_status("not_tx")
    assert result["status"]== "not_found"
    assert "transaction not found" in result["message"].lower()
    result = gateway.verify_payment_status("txn_921")
    assert result["transaction_id"]== "txn_921"
    assert result["status"] =="completed"
    assert result["amount"] ==10.50 
    