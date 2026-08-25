/**
 * Invocable entry for a Lead record-triggered Flow:
 * when Lead.Initial_Call_Completed__c becomes true, set AC field 41 so
 * automation "Website - Candidate — Initial Call Completed" can send Pre-Core.
 */
public with sharing class ActiveCampaignInitialCallAction {
    public class Request {
        @InvocableVariable(required=true label='Lead Id')
        public Id leadId;
    }

    public class Result {
        @InvocableVariable(label='Success')
        public Boolean success;
        @InvocableVariable(label='Message')
        public String message;
        @InvocableVariable(label='ActiveCampaign Contact Id')
        public String activeCampaignContactId;
        @InvocableVariable(label='Lead Email')
        public String email;
    }

    @InvocableMethod(
        label='Sync Initial Call Completed to ActiveCampaign'
        description='Sets AC INITIAL_CALL_COMPLETED (field 41) to true for the Lead email.'
        category='ActiveCampaign'
    )
    public static List<Result> sync(List<Request> requests) {
        List<Result> results = new List<Result>();
        if (requests == null || requests.isEmpty()) {
            return results;
        }

        Set<Id> leadIds = new Set<Id>();
        for (Request req : requests) {
            if (req != null && req.leadId != null) {
                leadIds.add(req.leadId);
            }
        }

        Map<Id, Lead> leads = new Map<Id, Lead>(
            [
                SELECT Id, Email, Initial_Call_Completed__c
                FROM Lead
                WHERE Id IN :leadIds
            ]
        );

        for (Request req : requests) {
            Result result = new Result();
            results.add(result);

            if (req == null || req.leadId == null) {
                result.success = false;
                result.message = 'Lead Id is required.';
                continue;
            }

            Lead lead = leads.get(req.leadId);
            if (lead == null) {
                result.success = false;
                result.message = 'Lead not found: ' + req.leadId;
                continue;
            }

            result.email = lead.Email;
            if (String.isBlank(lead.Email)) {
                result.success = false;
                result.message = 'Lead has no Email; cannot match ActiveCampaign contact.';
                continue;
            }
            if (lead.Initial_Call_Completed__c != true) {
                result.success = false;
                result.message = 'Lead.Initial_Call_Completed__c is not true; skipping AC write.';
                continue;
            }

            try {
                ActiveCampaignService.ContactMatch match = ActiveCampaignService.findContactByEmail(
                    lead.Email
                );
                if (match == null) {
                    result.success = false;
                    result.message =
                        'No ActiveCampaign contact for ' +
                        lead.Email +
                        '. Create/sync the contact in AC first.';
                    continue;
                }

                ActiveCampaignService.setInitialCallCompleted(match.id, true);
                result.success = true;
                result.activeCampaignContactId = match.id;
                result.message = 'Set INITIAL_CALL_COMPLETED=true on AC contact ' + match.id;
            } catch (Exception e) {
                result.success = false;
                result.message = e.getMessage();
            }
        }

        return results;
    }
}
