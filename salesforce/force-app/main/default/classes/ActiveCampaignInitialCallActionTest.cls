@IsTest
private class ActiveCampaignInitialCallActionTest {
    /**
     * Routes AC v3 calls by method + path. Toggle flags to exercise branches:
     *  - contactFound=false  → /contacts returns empty
     *  - existingValue=true  → contact fieldValues already has field 41 (PUT path)
     *  - failWrite=true      → the fieldValues write returns 500
     */
    private class AcMock implements HttpCalloutMock {
        Boolean contactFound = true;
        Boolean existingValue = false;
        Boolean failWrite = false;

        public HTTPResponse respond(HTTPRequest req) {
            HttpResponse res = new HttpResponse();
            res.setHeader('Content-Type', 'application/json');
            String endpoint = req.getEndpoint();
            String method = req.getMethod();

            if (endpoint.contains('/contacts?') && method == 'GET') {
                res.setStatusCode(200);
                res.setBody(
                    contactFound
                        ? '{"contacts":[{"id":"132","email":"allie@service2software.org"}]}'
                        : '{"contacts":[]}'
                );
                return res;
            }
            if (endpoint.contains('/contacts/') && endpoint.endsWith('/fieldValues') && method == 'GET') {
                res.setStatusCode(200);
                res.setBody(
                    existingValue
                        ? '{"fieldValues":[{"id":"6307","field":"41","value":"||true||"}]}'
                        : '{"fieldValues":[]}'
                );
                return res;
            }
            if (endpoint.contains('/fieldValues') && (method == 'POST' || method == 'PUT')) {
                if (failWrite) {
                    res.setStatusCode(500);
                    res.setBody('{"message":"boom"}');
                    return res;
                }
                res.setStatusCode(method == 'POST' ? 201 : 200);
                res.setBody(
                    '{"fieldValue":{"id":"999","contact":"132","field":"41","value":"||true||"}}'
                );
                return res;
            }

            res.setStatusCode(404);
            res.setBody('{"message":"unexpected ' + endpoint + '"}');
            return res;
        }
    }

    private static Lead makeLead(Boolean completed, String email) {
        Lead lead = new Lead(
            FirstName = 'Allie',
            LastName = 'Test',
            Company = 'S2S',
            Email = email,
            Initial_Call_Completed__c = completed
        );
        insert lead;
        return lead;
    }

    private static ActiveCampaignInitialCallAction.Request reqFor(Id leadId) {
        ActiveCampaignInitialCallAction.Request req = new ActiveCampaignInitialCallAction.Request();
        req.leadId = leadId;
        return req;
    }

    private static List<ActiveCampaignInitialCallAction.Result> run(Id leadId) {
        return ActiveCampaignInitialCallAction.sync(
            new List<ActiveCampaignInitialCallAction.Request>{ reqFor(leadId) }
        );
    }

    @IsTest
    static void sync_createsFieldValue_whenNoneExists() {
        Lead lead = makeLead(true, 'allie@service2software.org');
        Test.setMock(HttpCalloutMock.class, new AcMock());

        Test.startTest();
        List<ActiveCampaignInitialCallAction.Result> results = run(lead.Id);
        Test.stopTest();

        System.assertEquals(1, results.size());
        System.assertEquals(true, results[0].success, results[0].message);
        System.assertEquals('132', results[0].activeCampaignContactId);
    }

    @IsTest
    static void sync_updatesFieldValue_whenAlreadyPresent() {
        Lead lead = makeLead(true, 'allie@service2software.org');
        AcMock mock = new AcMock();
        mock.existingValue = true;
        Test.setMock(HttpCalloutMock.class, mock);

        Test.startTest();
        List<ActiveCampaignInitialCallAction.Result> results = run(lead.Id);
        Test.stopTest();

        System.assertEquals(true, results[0].success, results[0].message);
    }

    @IsTest
    static void sync_skips_whenCheckboxFalse() {
        Lead lead = makeLead(false, 'allie@service2software.org');

        Test.startTest();
        List<ActiveCampaignInitialCallAction.Result> results = run(lead.Id);
        Test.stopTest();

        System.assertEquals(false, results[0].success);
        System.assert(results[0].message.contains('not true'), results[0].message);
    }

    @IsTest
    static void sync_fails_whenNoEmail() {
        Lead lead = makeLead(true, null);

        Test.startTest();
        List<ActiveCampaignInitialCallAction.Result> results = run(lead.Id);
        Test.stopTest();

        System.assertEquals(false, results[0].success);
        System.assert(results[0].message.contains('no Email'), results[0].message);
    }

    @IsTest
    static void sync_fails_whenNoAcContact() {
        Lead lead = makeLead(true, 'allie@service2software.org');
        AcMock mock = new AcMock();
        mock.contactFound = false;
        Test.setMock(HttpCalloutMock.class, mock);

        Test.startTest();
        List<ActiveCampaignInitialCallAction.Result> results = run(lead.Id);
        Test.stopTest();

        System.assertEquals(false, results[0].success);
        System.assert(results[0].message.contains('No ActiveCampaign contact'), results[0].message);
    }

    @IsTest
    static void sync_fails_whenAcWriteErrors() {
        Lead lead = makeLead(true, 'allie@service2software.org');
        AcMock mock = new AcMock();
        mock.failWrite = true;
        Test.setMock(HttpCalloutMock.class, mock);

        Test.startTest();
        List<ActiveCampaignInitialCallAction.Result> results = run(lead.Id);
        Test.stopTest();

        System.assertEquals(false, results[0].success);
        System.assert(results[0].message.contains('HTTP 500'), results[0].message);
    }

    @IsTest
    static void sync_returnsEmpty_forEmptyInput() {
        Test.startTest();
        List<ActiveCampaignInitialCallAction.Result> results = ActiveCampaignInitialCallAction.sync(
            new List<ActiveCampaignInitialCallAction.Request>()
        );
        Test.stopTest();
        System.assertEquals(0, results.size());
    }

    @IsTest
    static void service_findContact_requiresEmail() {
        Boolean threw = false;
        try {
            ActiveCampaignService.findContactByEmail('   ');
        } catch (ActiveCampaignService.ActiveCampaignException e) {
            threw = true;
        }
        System.assertEquals(true, threw);
    }

    @IsTest
    static void service_setField_rejectsFalse() {
        Boolean threw = false;
        try {
            ActiveCampaignService.setInitialCallCompleted('132', false);
        } catch (ActiveCampaignService.ActiveCampaignException e) {
            threw = true;
        }
        System.assertEquals(true, threw);
    }
}
