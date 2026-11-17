import ca.uhn.fhir.context.FhirContext;
import java.nio.file.Path;
import java.time.ZonedDateTime;
import org.hl7.fhir.instance.model.api.IBaseResource;
import org.hl7.fhir.r4.model.IdType;
import org.opencds.cqf.fhir.cr.measure.MeasureEvaluationOptions;
import org.opencds.cqf.fhir.cr.measure.common.MeasurePeriodValidator;
import org.opencds.cqf.fhir.cr.measure.common.MeasureReference;
import org.opencds.cqf.fhir.cr.measure.r4.R4DataRequirementsService;
import org.opencds.cqf.fhir.cr.measure.r4.R4MultiMeasureService;
import org.opencds.cqf.fhir.utility.repository.ig.IgRepository;

/**
 * Run Measure $evaluate-measure or $data-requirements with clinical-reasoning against a folder in IG
 * layout (input/resources, input/tests, input/vocabulary).
 * Usage: Evaluate ROOT evaluate MEASURE_ID PERIOD_START PERIOD_END REPORT_TYPE [SUBJECT]
 *        Evaluate ROOT data-requirements MEASURE_ID PERIOD_START PERIOD_END
 * Periods are ISO date-times with an offset (2025-01-01T00:00:00Z). REPORT_TYPE is subject,
 * subject-list or population. Prints the result as JSON, or the exception if the operation throws.
 */
public class Evaluate {
    public static void main(String[] a) throws Exception {
        FhirContext ctx = FhirContext.forR4Cached();
        ctx.setValidationSupport(new ca.uhn.fhir.context.support.DefaultProfileValidationSupport(ctx));
        IgRepository repo = new IgRepository(ctx, Path.of(a[0]));
        String mode = a[1], id = a[2];
        ZonedDateTime start = ZonedDateTime.parse(a[3]), end = ZonedDateTime.parse(a[4]);
        MeasureEvaluationOptions options = MeasureEvaluationOptions.defaultOptions();
        IBaseResource out;
        try {
            switch (mode) {
                case "evaluate" -> out = new R4MultiMeasureService(repo, options, null, new MeasurePeriodValidator())
                        .evaluate(new MeasureReference.ById(new IdType("Measure", id)), start, end,
                                a[5], a.length > 6 ? a[6] : null, null, null, null, null);
                case "data-requirements" -> out = new R4DataRequirementsService(repo, options)
                        .dataRequirements(new IdType("Measure", id), a[3], a[4]);
                default -> throw new IllegalArgumentException(mode);
            }
        } catch (Exception e) {
            System.out.println("THROWS " + e.getClass().getSimpleName() + ": " + e.getMessage());
            return;
        }
        System.out.println(ctx.newJsonParser().setPrettyPrint(true).encodeResourceToString(out));
    }
}
