VersionNumbers = {'14.0'}; % Placeholder value
if ~ispc
    supportedCompilerInstalled = false;
else
    installed_compilers = mex.getCompilerConfigurations('C', 'Installed');
    MSVC_InstalledVersions = regexp({installed_compilers.Name}, 'Microsoft Visual C\+\+ 20\d\d');
    MSVC_InstalledVersions = cellfun(@(a)~isempty(a), MSVC_InstalledVersions);
    if ~any(MSVC_InstalledVersions)
        supportedCompilerInstalled = false;
    else
        VersionNumbers = {installed_compilers(MSVC_InstalledVersions).Version}';
        supportedCompilerInstalled = true;
    end
end


tc = my_msvc_32bit_tc(VersionNumbers{end});
save my_msvc_32bit_tc tc;