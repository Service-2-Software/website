/**
 * Thin ActiveCampaign v3 client for the Initial Call Completed → Pre-Core bridge.
 * Callouts go through Named Credential ActiveCampaign_API (Api-Token header).
 */
public with sharing class ActiveCampaignService {
    public class ActiveCampaignException extends Exception {
    }

    @TestVisible
    private static String namedCredentialDeveloperName = 'ActiveCampaign_API';
    @TestVisible
    private static String initialCallCompletedFieldId = '41';
    @TestVisible
    private static String initialCallCompletedTrueValue = 'true';

    public class ContactMatch {
        public String id;
        public String email;
    }

    public static ContactMatch findContactByEmail(String email) {
        if (String.isBlank(email)) {
            throw new ActiveCampaignException('Email is required to find an ActiveCampaign contact.');
        }

        String path =
            '/contacts?' +
            EncodingUtil.urlEncode('email', 'UTF-8') +
            '=' +
            EncodingUtil.urlEncode(email.trim(), 'UTF-8');
        Map<String, Object> body = (Map<String, Object>) JSON.deserializeUntyped(httpGet(path));
        List<Object> contacts = (List<Object>) body.get('contacts');
        if (contacts == null || contacts.isEmpty()) {
            return null;
        }

        Map<String, Object> first = (Map<String, Object>) contacts[0];
        ContactMatch match = new ContactMatch();
        match.id = String.valueOf(first.get('id'));
        match.email = String.valueOf(first.get('email'));
        return match;
    }

    /**
     * Upserts INITIAL_CALL_COMPLETED (field 41). AC normalizes checkbox posts of
     * "true" to the stored option form ||true||.
     */
    public static void setInitialCallCompleted(String contactId, Boolean completed) {
        if (String.isBlank(contactId)) {
            throw new ActiveCampaignException('ActiveCampaign contact id is required.');
        }
        if (completed != true) {
            throw new ActiveCampaignException(
                'Only true is supported for Initial Call Completed (Pre-Core send path).'
            );
        }

        String existingId = findFieldValueId(contactId, initialCallCompletedFieldId);
        Map<String, Object> fieldValue = new Map<String, Object>{
            'contact' => contactId,
            'field' => initialCallCompletedFieldId,
            'value' => initialCallCompletedTrueValue
        };
        String payload = JSON.serialize(new Map<String, Object>{ 'fieldValue' => fieldValue });

        if (String.isBlank(existingId)) {
            httpWrite('POST', '/fieldValues', payload);
        } else {
            httpWrite('PUT', '/fieldValues/' + existingId, payload);
        }
    }

    private static String findFieldValueId(String contactId, String fieldId) {
        Map<String, Object> body = (Map<String, Object>) JSON.deserializeUntyped(
            httpGet('/contacts/' + contactId + '/fieldValues')
        );
        List<Object> values = (List<Object>) body.get('fieldValues');
        if (values == null) {
            return null;
        }
        for (Object row : values) {
            Map<String, Object> fv = (Map<String, Object>) row;
            if (String.valueOf(fv.get('field')) == fieldId) {
                return String.valueOf(fv.get('id'));
            }
        }
        return null;
    }

    private static String httpGet(String path) {
        HttpRequest req = baseRequest(path);
        req.setMethod('GET');
        return send(req);
    }

    private static String httpWrite(String method, String path, String jsonBody) {
        HttpRequest req = baseRequest(path);
        req.setMethod(method);
        req.setHeader('Content-Type', 'application/json');
        req.setBody(jsonBody);
        return send(req);
    }

    private static HttpRequest baseRequest(String path) {
        HttpRequest req = new HttpRequest();
        req.setEndpoint('callout:' + namedCredentialDeveloperName + path);
        req.setHeader('Accept', 'application/json');
        // Merge field requires Named Credential "Allow Merge Fields in HTTP Header".
        req.setHeader('Api-Token', '{!$Credential.Password}');
        req.setTimeout(20000);
        return req;
    }

    private static String send(HttpRequest req) {
        HttpResponse res = new Http().send(req);
        Integer code = res.getStatusCode();
        if (code < 200 || code >= 300) {
            throw new ActiveCampaignException(
                'ActiveCampaign HTTP ' + code + ': ' + res.getBody()?.left(500)
            );
        }
        return res.getBody() == null ? '{}' : res.getBody();
    }
}
