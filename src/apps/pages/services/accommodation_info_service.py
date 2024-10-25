# from apps.accommodations.models import RefundPolicy
#
#
#
# # 환불정책
# class AccommodationRefundPolicyService:
#     def __init__(self, refund_policy_obj: RefundPolicy) -> None:
#         self.refund_policy_obj = refund_policy_obj.first()  # 첫 번째 환불정책만 사용
#         self.refund_policy_str = []
#
#     def refund_policy(self) -> list:
#         if self.refund_policy_obj:
#             # 환불 정책의 각 필드값을 가져오며, 이를 이용해 반환될 메시지를 구성
#             seven_days = f'체크인 기준 7일 전 18시까지: {int(self.refund_policy_obj.seven_days_before)}%'
#             self.refund_policy_str.append(seven_days)
#
#             five_days = f'체크인 기준 5일 전 18시까지: {int(self.refund_policy_obj.five_days_before)}%'
#             self.refund_policy_str.append(five_days)
#
#             three_days = f'체크인 기준 3일 전 18시까지: {int(self.refund_policy_obj.three_days_before)}%'
#             self.refund_policy_str.append(three_days)
#
#             one_day = f'체크인 기준 1일 전 18시까지: {int(self.refund_policy_obj.one_day_before)}%'
#             self.refund_policy_str.append(one_day)
#
#             same_day = f'당일 취소 및 No-show: {int(self.refund_policy_obj.same_day)}%'
#             self.refund_policy_str.append(same_day)
#
#             etc_policy = '취소, 환불 시 수수료가 발생할 수 있습니다.'
#             self.refund_policy_str.append(etc_policy)
#
#         return self.refund_policy_str
#
