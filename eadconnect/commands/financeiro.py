import uuid
import logging
from eadconnect.client import EducationAPI

logger = logging.getLogger(__name__)


async def exibir_financeiro(client: EducationAPI) -> None:
    """
    Simula o fluxo de recuperação de informações financeiras, débitos e criação de pagamento.
    
    Args:
        client (EducationAPI): Instância autenticada do cliente da API.
    """
    # 1. Launcher e token do app
    auth_app = client.auth_app_launcher()
    token_id = auth_app.get('redirectUrl', '').split('=')[-1]
    print(f"Token ID: {token_id}")
    
    me = client.get_me(token_id)
    app_access_token = me.get('accessToken')
    client.app_access_token = app_access_token
    print(f"App Access Token: {app_access_token}")

    # 2. Info do estudante
    get_my_info = client.get_my_info()
    print("Minhas Informações:", get_my_info)
    
    enrollments = get_my_info.get('enrollments', [])
    if not enrollments:
        logger.warning("Nenhuma matrícula encontrada.")
        return
        
    register = enrollments[0].get('academicRecord')
    enrollment_id = enrollments[0].get('id')
    print("Registro Acadêmico:", register)

    # 3. Débitos pendentes
    pending_debts = client.get_debts(register)
    print("Débitos pendentes:", pending_debts)
    
    results = pending_debts.get('results', [])
    if not results:
        logger.info("Nenhum débito pendente.")
        return
        
    # Obtém dados para simular a criação de pagamento
    first_debt = results[0]
    contract_id = first_debt.get('contracts', [{}])[0].get('id')

    # Descomente para obter o boleto/contrato específico
    # contracts = client.get_contract_slip(contract_id=contract_id)
    # print(contracts)

    # Descomente para verificar métodos de pagamento e configurações
    # payment_methods = client.get_payment_methods()
    # print(payment_methods)
    # payment_settings = client.get_payment_settings()
    # print(payment_settings)

    # 4. Criando intenção de pagamento via PIX (exemplo)
    order_id = str(uuid.uuid4())
    customer_id = get_my_info.get('student', {}).get('id')
    
    payload = {
        "orderId": order_id,
        "customerId": customer_id,
        "charge": {
            "amount": first_debt.get('dueValue', 100)
        },
        "debtReferences": [
            {
                "id": first_debt.get('id'),
                "dueDate": first_debt.get('dueDate'),
                "dueValue": first_debt.get('dueValue'),
                "originalValue": first_debt.get('originalValue'),
                "interestValue": first_debt.get('interestValue', "0.00"),
                "finesValue": first_debt.get('finesValue', "0.00"),
                "interestAndFines": first_debt.get('interestAndFines', "0"),
                "officeValue": first_debt.get('officeValue', "0"),
                "conditionalDiscountValue": first_debt.get('conditionalDiscountValue', "0"),
                "unconditionalDiscountValue": first_debt.get('unconditionalDiscountValue', "0"),
                "totalDiscountEventValue": first_debt.get('totalDiscountEventValue', "0"),
                "fitForAgreement": first_debt.get('fitForAgreement', False),
                "isOverdue": first_debt.get('isOverdue', False),
                "paymentValue": first_debt.get('paymentValue', "0"),
                "paymentDate": first_debt.get('paymentDate'),
                "paymentMethod": first_debt.get('paymentMethod'),
                "debtNumber": first_debt.get('debtNumber'),
                "competencyYear": first_debt.get('competencyYear'),
                "competencyMonth": first_debt.get('competencyMonth'),
                "correctionsValue": first_debt.get('correctionsValue', "0.00"),
                "additionsValue": first_debt.get('additionsValue', "0.00"),
                "discountsValue": first_debt.get('discountsValue', "0.00"),
                "externalId": first_debt.get('externalId'),
                "invoice": first_debt.get('invoice'),
                "paymentMethodTypes": first_debt.get('paymentMethodTypes', ["bank_slip", "credit_card", "pix"]),
                "warningAgreement": first_debt.get('warningAgreement', False),
                "contracts": first_debt.get('contracts', []),
                "debtStatus": first_debt.get('debtStatus', {}),
                "debtType": first_debt.get('debtType', {}),
                "financialResponsiblePerson": first_debt.get('financialResponsiblePerson', {}),
                "bankSlip": first_debt.get('bankSlip', {}),
                "waitingAgreementIntegration": first_debt.get('waitingAgreementIntegration', False),
                "viewPaymentsMethods": True,
                "selected": False
            }
        ],
        "enrollmentId": enrollment_id
    }
    
    brcode = client.create_payment(
        registration_number=register,
        payment_data=payload
    )
    print("Resultado do pagamento:", brcode)
