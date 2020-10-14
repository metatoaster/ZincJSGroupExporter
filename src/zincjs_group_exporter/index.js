var physiomeportal = require("physiomeportal");

var main = function()  {
  var UIIsReady = true;
  var organViewer = undefined;

  /**
   * Initialise all the panels required for PJP to function correctly.
   * Modules used incude - {@link PJP.ModelsLoader}, {@link PJP.BodyViewer},
   * {@link PJP.OrgansViewer}, {@link PJP.TissueViewer}, {@link PJP.CellPanel}
   * and {@link PJP.ModelPanel}.
   */
  var initialiseMain = function() {
      organViewer = new physiomeportal.OrgansViewer();
      var parent = document.getElementById("MAPcorePortalArea");
      var model_root = parent.getAttribute('data-model');
      var view_json = parent.getAttribute('data-view') || "./view.json";
      var organViewerDialog = new physiomeportal.OrgansViewerDialog(organViewer, parent);
      organViewer.setName("organViewer");
      organViewerDialog.setPosition(0, 0);
      organViewerDialog.setWidth("100%");
      organViewerDialog.setHeight("100%");
      organViewerDialog.hideCloseButton();
      organViewerDialog.dock();
      organViewerDialog.hideTitlebar();
      organViewerDialog.destroyModuleOnClose = true;
      organViewer.loadOrgansFromURL(model_root, undefined, undefined, "heart", view_json);

      parent.organViewer = organViewer;
      parent.organViewerDialog = organViewerDialog;
  }

  var initialise = function() {
    initialiseMain();
  }

  initialise();
}

var createVisualisation = function() {
    var myModule = new main();
}

window.document.addEventListener('DOMContentLoaded', createVisualisation);
