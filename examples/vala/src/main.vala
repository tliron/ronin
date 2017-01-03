using Gtk;

public int main (string[] args) {
    Gtk.init (ref args);

    var window = new SyncSample ();
    window.show_all ();

    Gtk.main ();
    return 0;
}