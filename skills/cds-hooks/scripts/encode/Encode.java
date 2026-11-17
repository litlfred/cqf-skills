import ca.uhn.fhir.context.FhirContext;
import com.fasterxml.jackson.databind.ObjectMapper;
import com.fasterxml.jackson.databind.SerializationFeature;
import com.fasterxml.jackson.annotation.JsonInclude;
import java.nio.file.Path;
import java.util.List;
import org.hl7.fhir.instance.model.api.IBaseParameters;
import org.hl7.fhir.instance.model.api.IBaseResource;
import org.hl7.fhir.r4.model.IdType;
import org.opencds.cqf.fhir.cr.hapi.cdshooks.CdsResponseEncoderService;
import org.opencds.cqf.fhir.cr.hapi.cdshooks.discovery.CrDiscoveryService;
import org.opencds.cqf.fhir.cr.plandefinition.PlanDefinitionProcessor;
import org.opencds.cqf.fhir.utility.monad.Eithers;
import org.opencds.cqf.fhir.utility.repository.ig.IgRepository;

/**
 * What clinical-reasoning's CDS Hooks service makes of a PlanDefinition, on a folder in IG layout.
 * Usage: Encode ROOT discovery PLAN_DEFINITION_ID
 *        Encode ROOT response PLAN_DEFINITION_ID SUBJECT
 *        Encode ROOT apply PLAN_DEFINITION_ID SUBJECT
 * discovery prints the discovery document for that one PlanDefinition; response runs $r5.apply for SUBJECT (what the R4 CDS
 * service does) and prints the CDS Hooks response it encodes; apply prints the $r5.apply result
 * itself. Prints the exception if one is thrown (with ENCODE_TRACE set, its stack trace).
 */
public class Encode {
    public static void main(String[] a) throws Exception {
        FhirContext ctx = FhirContext.forR4Cached();
        ctx.setValidationSupport(new ca.uhn.fhir.context.support.DefaultProfileValidationSupport(ctx));
        IgRepository repo = new IgRepository(ctx, Path.of(a[0]));
        ObjectMapper om = new ObjectMapper().enable(SerializationFeature.INDENT_OUTPUT)
                .disable(SerializationFeature.FAIL_ON_EMPTY_BEANS)
                .setSerializationInclusion(JsonInclude.Include.NON_EMPTY);
        Object out;
        try {
            switch (a[1]) {
                case "discovery" -> {
                    // As GET {baseUrl}/cds-services returns it: {"services": [...]}, empty when the
                    // PlanDefinition is not a service.
                    var service = new CrDiscoveryService(new IdType("PlanDefinition", a[2]), repo).resolveService();
                    if (service == null) {
                        System.out.println("{\n  \"services\" : [ ]\n}");
                        return;
                    }
                    out = java.util.Map.of("services", List.of(service));
                }
                case "response", "apply" -> {
                    IBaseParameters applied = new PlanDefinitionProcessor(repo).applyR5(
                            Eithers.forMiddle3(new IdType("PlanDefinition", a[2])), List.of(a[3]),
                            null, null, null, null, null, null, null, null, null, true, null, null,
                            (IBaseResource) null, (IBaseResource) null, (IBaseResource) null);
                    if (a[1].equals("apply")) {
                        System.out.println(ctx.newJsonParser().setPrettyPrint(true).encodeResourceToString(applied));
                        return;
                    }
                    out = new CdsResponseEncoderService(repo).encodeResponse(applied);
                }
                default -> throw new IllegalArgumentException(a[1]);
            }
        } catch (Exception e) {
            System.out.println("THROWS " + e.getClass().getSimpleName() + ": " + e.getMessage());
            if (System.getenv("ENCODE_TRACE") != null) e.printStackTrace(System.out);
            return;
        }
        System.out.println(out == null ? "null" : om.writeValueAsString(out));
    }
}
