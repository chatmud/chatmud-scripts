"destructures a moo database into a directory.";
"Very basic and only includes objects with directly-defined verbs and props; intended to be a tool for dumping a database that doesn't seem to want to cooperate (looking at you improvise)";
tool_name = "MOO database decomposer";
tool_version= "0.1";
output_directory = "decomposed_database";
shutdown_after = true;
progress_update_interval = 2;
last_progress_update = 0;
server_log(tostr(tool_name, ", version ", tool_version, "."));
server_log(tostr("Will write dumps to: ", output_directory, "."));
suspend(3);
core = [];
server_log("Identifying core objects...");
for p in (properties(#0))
  v = #0.(p);
  t = typeof(v);
  if (t != OBJ)
    continue;
  elseif (t == OBJ)
    core[p] = v;
  endif
  yin();
endfor
server_log(tostr("Discovered ", length(mapkeys(core)), " core objects."));
to_process = {};
verbs = properties = skipped_properties = lines = 0;
server_log("Scanning for objects to process...");
scan_started_at = ftime(1);
for o in [#0 .. max_object()]
  if (time() - last_progress_update > progress_update_interval)
    server_log(tostr("Scanning ", toint(o), " / ", toint(max_object()), "."));
    last_progress_update = time();
  endif
  if (valid(o))
    if (properties(o) || verbs(o))
      to_process = {@to_process, o};
    endif
  endif
  yin();
endfor
scan_finished_at = ftime(1);
server_log(tostr("Finished collecting interesting objects: ", length(to_process), " found in ", floatstr(scan_finished_at - scan_started_at, 2), "s."));
data = [];
server_log("Gathering verbs and properties...");
started_collecting_at = ftime(1);
for o in (to_process)
  if (time() - last_progress_update > progress_update_interval)
    server_log(tostr("Gathering: ", toint(o), " / ", toint(max_object()), "."));
    last_progress_update = time();
  endif
  objdata = [];
  objdata["name"] = `o.name ! ANY => "<unknown>"';
  objdata["owner_id"] = o.owner;
  objdata["owner_name"] = `o.owner.name ! ANY => "<unknown>"';
  objdata["parents"] = parents(o);
  objverbs = verbs(o);
  objprops = properties(o);
  if (objverbs)
    objdata["verbs"] = {};
    verbs = verbs + length(objverbs);
  endif
  if (objprops)
    objdata["properties"] = {};
    properties = properties + length(objprops);
  endif
  for v, v_index in (objverbs)
    vinfo = verb_info(o, v_index);
    vargs = verb_args(o, v_index);
    code = verb_code(o, v_index);
    lines = lines + length(code);
    vdata = ["args" -> vargs, "code" -> code, "perms" -> vinfo[2], "name" -> v, "owner_name" -> `vinfo[1] ! ANY => "<unknown>"', "owner_wizard" -> vinfo[1].wizard, "owner_programmer" -> vinfo[1].programmer, "owner_id" -> vinfo[1]];
    objdata["verbs"] = {@objdata["verbs"], vdata};
    yin();
  endfor
  for p, p_index in (objprops)
    value = o.(p);
    valtype = typeof(value);
    if (valtype in {anon, waif} || (valtype == LIST && value && typeof(value[1]) in {ANON, WAIF}) || (valtype == MAP && value && typeof(value[mapkeys(value)[1]]) in {ANON, WAIF}))
      "Don't include waifs and anons for now.";
      skipped_properties = skipped_properties + 1;
      server_log(tostr("Skipping ", o, ".", p, " because it is either an anon, a waif, or a structure containing either and we don't serialize those yet."));
      continue;
    endif
    pinfo = property_info(o, p);
    pdata = ["name" -> p, "owner_name" -> ` pinfo[1].name ! ANY => "<unknown>"', "owner_wizard" -> pinfo[1].wizard, "owner_programmer" -> pinfo[1].programmer, "perms" -> pinfo[2], "value" -> value];
    objdata["properties"] = {@objdata["properties"], pdata};
  endfor
  data[o] = objdata;
  yin();
endfor
finished_collecting_at = ftime(1);
server_log(tostr("Finished gathering data in ", floatstr(finished_collecting_at - started_collecting_at, 2), "s."));
server_log(tostr("Gathered and will dump: ", length(to_process), " objects, ", verbs, " verbs (", lines, " lines in total) and ", properties, " properties."));
if (skipped_properties)
  server_log(tostr("Skipping ", skipped_properties, " properties with value either an anon or waif."));
endif
dirstat = `file_stat(output_directory) ! ANY';
if (dirstat == E_FILE)
  server_log("Creating output directory...");
  file_mkdir(output_directory);
  server_log("Directory created.");
elseif (file_list(output_directory))
  server_log("Warning: output directory is not empty, may be mixing in results from a previous run of this script.");
endif
other_paths = {output_directory + "/core_objects", output_directory + "/other_objects"};
for p in (other_paths)
  if (`file_stat(p) ! ANY' == E_FILE)
    server_log(tostr("Creating directory '", p, "'..."));
    file_mkdir(p);
    server_log("Created.");
  endif
endfor
suspend(1);
server_log("Beginning serialization...");
serialization_started_at = ftime(1);
for od, o in (data)
  if (time() - last_progress_update > progress_update_interval)
    current_index = o in mapkeys(data);
    server_log(tostr("Plain-text serializing: ", current_index, " / ", length(mapkeys(data)), "."));
    last_progress_update = time();
  endif
  objlines = {};
  "Plain-text dump format starts with an @create command invocation, so figure out the ref we're going to use.";
  is_core = o in mapvalues(core);
  if (!od["parents"])
    "Object has no parents. Use #-1.";
    ref = "#-1";
  else
    "Object has one or more parents. Represent them all.";
    "The output here is intended to be like #1,#2,#3 for an object with those IDs as it's parents, or $box,$bag,$thing for core refs.";
    ref = "";
    for p in (od["parents"])
      if ((i = p in mapvalues(core)))
        ref = tostr(ref != "" ? ref + "," | "", "$", mapkeys(core)[i]);
      else
        ref = tostr(ref != "" ? ref + "," | "", p);
      endif
      yin();
    endfor
  endif
  objlines = {@objlines, tostr("@create ", ref, " called \"", od["name"], "\"")};
  if (maphaskey(od, "properties"))
    for pd in (od["properties"])
      "Introduce with @property...";
      p = pd["name"];
      introline = tostr("@property ", o, ".", p, " \"", pd["perms"], "\"");
      valline = tostr(";", o, ".(\"", p, "\") = ", toliteral(pd["value"]));
      objlines = {@objlines, introline, valline};
      yin();
    endfor
  endif
  if (maphaskey(od, "verbs"))
    for vd in (od["verbs"])
      "Introduce each verb with an @verb invocation, including it's arguments and bits.";
      vref = tostr(o, ":\"", vd["name"], "\"");
      introline = tostr("@verb ", vref, " ", vd["args"][1], " ", vd["args"][2], " ", vd["args"][3], " ", vd["perms"]);
      "Then an @program script...";
      progscript = {tostr("@program ", vref), @vd["code"], "."};
      objlines = {@objlines, introline, @progscript, ""};
      yin();
    endfor
  endif
  "Now we have our lines in `objlines`, open a file for this object and write them out.";
  "Make path, but don't include an extension.";
  "Also clean out slashes and commas from object names.";
  clean_objname = od["name"];
  clean_objname = strsub(clean_objname, ",", "");
  clean_objname = strsub(clean_objname, "/", "--");
  path = tostr(output_directory, "/", is_core ? "core_objects" | "other_objects", "/", o, " - ", clean_objname);
  handle = file_open(path + ".moo", "w+tf");
  for line in (objlines)
    file_writeline(handle, line);
    yin();
  endfor
  file_close(handle);
  "Now dump the json representation of data we've collected as well.";
  try
    jsondata = generate_json(od);
  except e (ANY)
    server_log(tostr("Encountered an error when generating json representation for object ", o, ": ", od["name"], "."));
    server_log(toliteral(e));
    server_log("Literal of the offending data map:");
    server_log(toliteral(od));
    return;
  endtry
  handle = file_open(path + ".json", "w-tf");
  file_write(handle, jsondata);
  file_close(handle);
  yin();
endfor
serialization_finished_at = ftime(1);
server_log(tostr("Finished serializing ", length(mapkeys(data)), " objects in ", floatstr(serialization_finished_at - serialization_started_at, 2), "s."));
server_log("All done!");
if (shutdown_after)
  shutdown(tostr("Finished running ", tool_name, " version ", tool_version, "."));
endif