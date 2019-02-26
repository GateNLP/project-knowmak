// Warning: this has to alter the inputAS; the outputAS is ignored.


// Delete SelectedToken and MultiWord annotations that span
// or subspan NEs and Addresses.

Set<String> exclusionTypes = ["Person", "Organization", "Location",
    "Date", "Money", "Percent", "Address", "UserID", "Number"] as Set;

AnnotationSet candidates = inputAS.get("MultiWord");

AnnotationSet excluded = inputAS.get(exclusionTypes);
//AnnotationSet strongStop = inputAS.get("StrongStop");

for (Annotation candidate : candidates) {
  // delete unwanted term candidates
  if (! gate.Utils.getCoveringAnnotations(excluded, candidate).isEmpty()) {
    FeatureMap newf = Factory.newFeatureMap();
    newf.putAll(candidate.getFeatures());
    String newType = "deleted_NE_" + candidate.getType();
    inputAS.add(candidate.getStartNode(), candidate.getEndNode(), newType, newf);
    inputAS.remove(candidate);  
  }
  
//  else if (! gate.Utils.getContainedAnnotations(strongStop, candidate).isEmpty()) {
//    FeatureMap newf = Factory.newFeatureMap();
//    newf.putAll(candidate.getFeatures());
//    String newType = "deleted_SS_" + candidate.getType();
//    inputAS.add(candidate.getStartNode(), candidate.getEndNode(), newType, newf);
//    inputAS.remove(candidate);  
//  }
  
}



// Delete extra MultiWord annotations with exactly the same span
// (keep one of each group)

List<Annotation> mwList = Utils.inDocumentOrder(inputAS.get("MultiWord"));

for (int i=0 ; i < mwList.size() - 1 ; i++) {
  Annotation mwi = mwList.get(i);
  
  for (int j=i+1 ; j < mwList.size() ; j++) {
    Annotation mwj = mwList.get(j);
    
    if (Utils.start(mwj) > Utils.start(mwi)) {
       //if we've moved past the start offset of the outer annotation then
       //because the annotations are sorted we know we'll never find a matching
       //one so we can safely stop looking.
       break;
    }

    if ( ( Utils.start(mwj) == Utils.start(mwi) )
        && ( Utils.end(mwj) == Utils.end(mwi) ) ) {
      inputAS.remove(mwj);
    }
  }
}
