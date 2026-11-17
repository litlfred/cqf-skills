import ca.uhn.fhir.context.FhirContext;
import java.nio.file.Path;
import java.util.Arrays;
import java.util.List;
import org.hl7.fhir.instance.model.api.IBaseParameters;
import org.hl7.fhir.r4.model.IdType;
import org.opencds.cqf.fhir.cql.EvaluationSettings;
import org.opencds.cqf.fhir.cql.engine.retrieve.RetrieveSettings.TERMINOLOGY_FILTER_MODE;
import org.opencds.cqf.fhir.cr.CrSettings;
import org.opencds.cqf.fhir.cr.library.LibraryProcessor;
import org.opencds.cqf.fhir.utility.monad.Eithers;
import org.opencds.cqf.fhir.utility.repository.ig.IgRepository;

/**
 * Run Library $evaluate with clinical-reasoning against a folder in IG layout (input/resources,
 * input/tests, input/vocabulary), so that retrieves and `in` use the ValueSets found there.
 * Usage: Evaluate ROOT LIBRARY_ID SUBJECT [MODE [EXPRESSION...]]
 *   MODE is the retrieve's terminology filter: auto (the default), value-set-url, inline-codes or
 *   in-memory. With EXPRESSIONs, only those definitions are evaluated, each on its own run, so that
 *   one failing definition does not hide the others.
 * Prints the Parameters as JSON, or the exception if the operation throws.
 */
public class Evaluate {
    public static void main(String[] a) throws Exception {
        FhirContext ctx = FhirContext.forR4Cached();
        ctx.setValidationSupport(new ca.uhn.fhir.context.support.DefaultProfileValidationSupport(ctx));
        IgRepository repo = new IgRepository(ctx, Path.of(a[0]));
        TERMINOLOGY_FILTER_MODE mode = switch (a.length > 3 ? a[3] : "auto") {
            case "auto" -> TERMINOLOGY_FILTER_MODE.AUTO;
            case "value-set-url" -> TERMINOLOGY_FILTER_MODE.USE_VALUE_SET_URL;
            case "inline-codes" -> TERMINOLOGY_FILTER_MODE.USE_INLINE_CODES;
            case "in-memory" -> TERMINOLOGY_FILTER_MODE.FILTER_IN_MEMORY;
            default -> throw new IllegalArgumentException(a[3]);
        };
        EvaluationSettings es = EvaluationSettings.getDefault();
        es.getRetrieveSettings().setTerminologyParameterMode(mode);
        CrSettings settings = CrSettings.getDefault().withEvaluationSettings(es);
        List<String> exprs = a.length > 4 ? Arrays.asList(a).subList(4, a.length) : List.of();
        for (List<String> one : exprs.isEmpty() ? List.<List<String>>of(List.of()) : exprs.stream().map(List::of).toList()) {
            IBaseParameters out;
            try {
                out = new LibraryProcessor(repo, settings).evaluate(
                        Eithers.forMiddle3(new IdType("Library", a[1])), a[2],
                        one.isEmpty() ? null : one, null, true, null, null,
                        (org.hl7.fhir.instance.model.api.IBaseResource) null, null, null);
            } catch (Exception e) {
                System.out.println("THROWS " + e.getClass().getSimpleName() + ": " + e.getMessage());
                continue;
            }
            System.out.println(ctx.newJsonParser().setPrettyPrint(true).encodeResourceToString(out));
        }
    }
}
