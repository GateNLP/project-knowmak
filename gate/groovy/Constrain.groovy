import org.apache.commons.lang.StringEscapeUtils;
import org.apache.commons.lang.StringUtils;
import java.lang.Math;


knowmaks = inputAS.get("Knowmak");

for (knowmak in knowmaks) {
    klength = Utils.length(knowmak);
    covers = new HashSet<Annotation>(Utils.getCoveringAnnotations(inputAS, knowmak, "Knowmak"));
    covers.remove(knowmak);
    // 1. Remove a Knowmak annotation contained within a larger one.
    // 2. Remove a duplicate with the same span and uri.
    for (cover in covers) {
        if ( (Utils.length(cover) > klength) ||
             ( (Utils.length(cover) == klength) && 
               cover.getFeatures().get("uri").equals(knowmak.getFeatures().get("uri") ) ) ) {
           inputAS.remove(knowmak);
           break;
        }
    }
}
