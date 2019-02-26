// Remove duplicate annotations

import gate.*;
import java.util.*;

// TODO: remove coextensive annotations and all those which are contained, also the ones 
// overlapping with the current one. NOTE: as soon as an annotation gets added to the set
// scheduled for removal, do not process that annotation in the main loop any more!
@Override
public void execute() {

  String anntype = (String)parms.get("annotationType");
  Set<Annotation> toRemove = new HashSet<Annotation>();
  AnnotationSet anns = inputAS.get(anntype);
  for(Annotation ann : anns) {
    // if this annotation has been scheduled for removal, skip it
    if(toRemove.contains(ann)) continue;
    // the annotation needs to get processed, so lets get all overlapping ones (this includes
    // the coextensive in contained ones)
    AnnotationSet overlappings = gate.Utils.getOverlappingAnnotations(anns, ann);
    // add the overlapping ones to the ones to be removed but check we do not add the current one
    // NOTE: this is clumsier than adding to a set and removing the current one before adding
    // the set to toRemove, but should be as fast and avoid unneeded memory allocation
    for(Annotation overlapping : overlappings) {
      if(overlapping != ann) toRemove.add(overlapping);
    }
  }
  
  inputAS.removeAll(toRemove);
}
