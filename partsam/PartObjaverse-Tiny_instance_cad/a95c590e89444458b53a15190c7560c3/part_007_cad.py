"""Standalone mesh-derived CAD code, with embedded vertex and triangle data.

This reconstructs a faceted BREP, not an inferred sketch/extrusion feature tree.
Original numeric coordinates are retained; physical STL units are unknown.
Open meshes remain CAD surfaces. No guessed closures or thickness are added.
Run: python part_XXX_cad.py [--output-directory PATH] [--no-validate]
"""
from pathlib import Path
import argparse,base64,io,json,time,zlib
import numpy as np
import cadquery as cq
from OCP.BRepBuilderAPI import BRepBuilderAPI_Sewing

PART_NAME = 'part_007'
SOURCE_INFO = {'source_path': '/data/home/cuiyuehan/project/mesh2cad/partsam/PartObjaverse-Tiny_instance_stl/a95c590e89444458b53a15190c7560c3/part_007.stl', 'relative_path': 'a95c590e89444458b53a15190c7560c3/part_007.stl', 'source_sha256': '321952de6f404d6d5a9255414dc5c83917b8e9ade57f0fd2af5619c3a03be036', 'input_faces': 300, 'input_vertices': 201, 'input_watertight': False, 'input_winding_consistent': True, 'input_bounds': [[-0.09893286228179932, -0.2461540699005127, -0.08370286226272583], [0.3139352798461914, 0.36307668685913086, 0.19434157013893127]]}
GEOMETRY_BASE85 = 'c$}r03shBQ8iqG2B;IeSf$339&=B#OnaI)1`vn!#yu={{(NqvHMN>D4qh=a~k{Niz@D_+jD2lQXL_<YPO)D$38m*=os~I(GYWDxV?-|cIG;7V8Ict6EefH~rzWx8-f7zR}3>jIwP74j6_S)_K4f;)Pu4yV7Xf3ptBI6QfMMTC2%!^HQ)0&8{K6XtVGjVjtb8gy8+7jOxk?|36zWpq|{iFK&`dfUXV&W3w!sms>#Lb9Q{*drF@sXw<9~~YWX<qyF2<+}}>Dk%evefcFe(I?{?43|ptTg@JxnNWD@vGktcJv2KIxp9`4<(2mI(<m_`uV?}R@c_Mdk;GL+NAy!a&2^+?C2ZQ*IZE7M!)C+CqFsxL%GiX>uS;BF$X2j)r2y+w*E8M(bqFlPRe!2%P%<k)-7LLl>F0r7C8EbKKGJb_X&7Qv^;IE<ZpcKth%nga_@wrZ%ul#O0LVs<w(2LIlD!#|7?gKxN2XpgRkeDE|Ke72}_;)y4O!hJxh0#IQm-K5ohGO<wB?Y*2T4?KGsOLQpfhz=tHPa{Lj0c+HWkqEdCFF%XezOsmn)l{bIcxsGrv^`QB$4GG61$BSpA>Os4eHy^HwPrSZk$r})CZv!GnA10wbmJNVlAIZ|g^k7FfH?YmZ^&fk8YA?<3lhTnY`?%Svb?i>B^M$|tBbzlF))?x?WaEq03S$#GhcWiI<Uxsm|{2n3gZ7W_A_0B#f{=tl$!H#~=N_@Y_FU864=W#{mWy|qACqJvd_}a~%c8hA8o<@Cpp)R{$i7j^YM}H#yG456!lIt0{n?(P-6yx;!@Es?=av}00l&mUt^v~y@4x#t59DTj&9P0l==>ezqI}&AG+2S(F9P{hR2V`C8w*udH%JW+c<~Pc#+^IjW#$cVVo9onGJ5?#Z<<nnJI<-IiE!N??@p(?|w_9aBSi*)l_s6RN*5@AYJ&x^-_95aMOFEP|wl_9@fcc$QT!?k_{O&)je}~Hb!GARGcHed0?Y`^0+kMx0e=XyH^v87_4hz7!=(>;Ye+S=nUwmF$)<uo|71a&C>%LgD|FEd*IYYn3Ib-)-&l&nP&J(-udT!W#*K;E+6Z7DDPX3sMak!q(^lO~Y^lO~Y^lO~YIgRB$HJ&f@Ydl}**Lc3zeb?uU?`7n1ecsu9*XLbbi?q{zZCa$(pFVvw*4@Y;e80nxW6HNa8i0As`CWYDT%8i-Z~N*T=F_KbCGxypEbUj;Li?EE@H4L+5r6$+_<2$ABXD2s=G3EdUA|X*{maMXzDC6p=y!Wh>9>*5@`T*CQ5X0zkBYB<u1S7l_gBa>$AWQQU2$CQduk;7oX+A~qXMP>#?BPX_rZS1<KFwI)WNO%i1=$VaNpLsa$mjP_qeaudE_5eiGKQ3q5Y;R<k{8Fka4Z3i}l&{68u+hOMXj4CD!wRYw&m8FO~Lzh45eW!THth>|wcYTr>3F@D*S8zKS~3dt2(S=XMs~>X9b*)h{2zzHZn9d4`}qdXJxE-RsNY>z6M|`|4$9(9c$(@XK3BKexrMkpAeSr@?P`sT6r^*dKY($nSST=Fyn_$PtWxiTK98wkM_iPJhX-|Nb)athdTKv3YOBe(3W$@?70nCimSJgmtwx6?uI8P|w@G7*}{2+IJp>_NVTlKUyCA_db+)x1CNz{$KNP-y8mCr9Z2>$@!p%9YWm#Mj(IeT=etpBHZ_Akkq+)M>q7x(|~{NuB@NxtO0T!=w~k=|DLJmWW5FaBIm4D`xE$e-#{Hao8cVMZla$RGo+u@exc}R#Vxe=sFwFr+e9zazs-Hz_v;wxkEQ<=oI`K7!8!QFY00ly4q*K}?jydQbi6|R&F$nI(BnJ7|M<N0U$=dL{tWPgzsg(Y#VDMJb6{v6<ZqKE`7LA9<vFVtJc;uttD*SYN@t>OlLnyuov?E0|HCP$Ti1c&Yws_R{MBdbW4)~$ggoDbNZs@+5958~9(;Yrmmf&~+quL4W-$ET^Q8aUrfQjYy;~Ua<Swt2`nS4)^WS?3{2!-_uX&cdCw@MBeSSCDzuOvqhdN(ei}pYHV4e5&kaJqQvmXA+%Q*Kg%|-niy@PSJ-G+0_<2%%?(=PZac~XDlYI8hq@^g`A^^G&qeuW2~i}450etCe@({^|$=F#^k`kB}p<Lz=+*1vwH2<<mq!@MW;!8uS>iu@b4V1AQ^v7hD06ZL|uH|<z9&at6qFkks4$a5?W?PpiQzaJ<2OPlr^)@K3zfG=df*sRM@|83Q{uaSWDRz50Q@>Jb}pE(oz<$4F~m(03&Zrx8hFY`5bDE7-g8pBU5mGz*dx50ZtaZ~uqlBJ)<y}x7Kj`kMcNH?UP#>ro?-cGke`$=Uu|Fg%z&$gg_>KfTcHm?kMztFaH5a0TZo6Ng)juq!j$z#Y9(5(XN%7*#!_lJL@yWCfA*%R|VxG((H?&8~K9Yoz`K7;%E4U>5{4)(-)j-4RB-ftr6*}Xl^vGz8!5A~JtR&Vc$y8SW>?GN6OePr3w0_)_HSop0=W#4JTuVbGsUI70>bMdX+s<EEWCnA6DMAZ4h?LE>ie=*vh`3U>2(Jl0|O)|#yb++U&J`F*hXV)Ol*U#X2+WQ2ar>kE@o&(-^PWg^Uos-w0&Ueqsc&&>IG2SUD$a7wk@mi|}BF`@yaNn1cPfPx?PB_OVWgySyo7mS|67ZfDy&wMlk7d5}$_%_Ox#gliw;#iN?M=mgd9#4)&0EH6-Tze{>ihxn#1%?=%l;eaXWMh|56_l$QtdVZ^BZvy`3L6V{BQXJ?)%#h7?($o)XnnkO3X|0UHG<kQa8(mRmd~;XXKeRLHeVA-3#^a@sPY<YKIds-ucJyeji#7@164#QMVQgWnT1G8i}vhIV#UPt>;L2|JOfni9FxW!gFm<DAv!N)@Z*H>%@|96Yt$mwG-buE(!fKZsG5&P2J(oeoK5?lm+L1P!RmE!BPh!@GRax+YE-kIT-us_X_wEhvUB18(8OF!;pVU2*%~J2<!0VGR*J(=i#4hi+LQHh<T|q7yh?dIDb6T<eb+75-{GU>*M*`-XHa;dIf&wyEt!?(lOrp>Bv+63+#&zTjfZ*#TDphz%-nbMSsCLx$FY`>DQ&6#`mQ-4~srS{>RgC{%1$xJ%8PO_&-+2IiQDjmvc|QQCI#>uzndU<Ekz^!Tr)oeEm*6%x_fBQ^6rlzshB%jvk!S$b8b6;i<LIqQV`1l2fMo*!7QplAG1*zxqk8XJFv}`;(m2>_cxef~md8O8bz5$$hC^$x0t5_azT7V<5FN^>K1%ay^FPCe*IvCgfJsZsb;EZ)zY}X$P`5xf!(`xf!`R)k0R<hTNRoni@b>>Q8P>Zc6P!Zc46C^&{6OH>P$XHzv2FK1Oay_M&zqca&uX_98cAC~nJ8>_hEHR@$Acv?tkz+=JSm+=KiS^=a}`<U!P-<U!;i)RE*N<Pp^2<Pqdy)Mv=U$b+d?veIC((!OM+1IUBP!?XwM&z^H2?>U4TL>)*DBKuN1lYPmJsP)K=$h8>qn>MwH_TZzq4z(4z4!JJXo2;}Mxh~n0+MKMkHCbs>vM1S{TA%DrcB3{XyOC>CTas&&AEJ7Zl{O@MGOxX#?i`al^V-Mg#u~UWul-Y-HLJ~h_8Kbopf)6XkQ-3jk{gg8rTUQjnen6<PnhwD84sJGj^q$Crke4B8E=~Lx*6N)D=(B9M^-wWoNmUeW@J&-^?K@B@_O<TY7$xLY;qxUlu-|p%gCpxr^xEN8`&47$>cclbgGT4@)wwKz>F=_oo1Xc<9##Asm0`S@=5A3@=5Yh>U-p)<UHzbavpgX^=<Ml@;>TY<bC7<>Q3@b_PK!lU(IoE;lHis7!R<1S>$wwF{d-OILyOZ=2=T$@pv<)Xjl_*ockn(;`!96<oV<%>J;)Q<_e)sC66^@v>6kr<H$-UktdR$Gh+tTMx8{qk*6~hhf>FpL&+hGaqQPP-dnMnceM_-QxB4r?jdg{tNo!<-=OXxA2OrFjC_V-gQ55oL$O-JrPLy73Au#1iWrJ>&DcuKq#hz?lDARw$?9H*d4Hwvl9i@8^exTdJ4#=nrjgZmv-mxwDP*N9$nTQv-%%P*T|riRU9F8dyjJJMJnAy?JaRa74tWm08_w}AVm*|;M&3%!rDl+oW|MQtMbzUCbw2JeCrZnx$F&D%k>Wyz;v8x=IfuNNnnB)7UdK?JNPUf*NS;MqM4m;CXDnikw^1{xi^vnq7-Posj4(6iQlrUp$uBV!+s_oG>g-he&Su6!YBD*QZ5C3a$up?WQKQMxy!Ueq#cF?#r9MjyBZsly&r-*b$5KaA$B@;!7|(G}Alv^<=_u-WvZ`l<8Ic<H?Q#u!S|`U)Una+pU!?wt{33Y)btQQLc`0=<c_}%Tnm~>v&!k3@XOgE;Bgjf8lP9xAcAmg%HO6?hRXUFxL7q$vCr>6%piUv%pX+L`tNp8<0rQz(^+~PScg)yp#wO|x@+R^cYASgRc@=d7Igz@Kx<PxeUliN-kz%#a3aJGQ#rvomv<J^q#k;7f<W%;_{w!8(e_ks-O5ID|ui<%c#Eg)UZnav}{!jnK<iSUmmpsS+aN_z+=RboTznNy{`u88jAtT+@yPo+XSWAi@uKse<{sr{$UaS'

def decode_geometry():
    with np.load(io.BytesIO(zlib.decompress(base64.b85decode(GEOMETRY_BASE85)))) as data:
        return data['vertices'],data['faces']

def build():
    vertices,faces=decode_geometry()
    center=(vertices.min(axis=0)+vertices.max(axis=0))/2
    extent=float(np.ptp(vertices,axis=0).max())
    if extent<=0: raise ValueError('Source has zero extent')
    construction_scale=100.0/extent
    v=(vertices-center)*construction_scale
    sewing=BRepBuilderAPI_Sewing(1e-7,True,True,True,False)
    planar_faces=[]
    skipped=[]
    for index,tri in enumerate(faces):
        points=v[tri]
        if np.linalg.norm(np.cross(points[1]-points[0],points[2]-points[0]))<=1e-12:
            skipped.append(index)
            continue
        wire=cq.Wire.makePolygon([cq.Vector(*p) for p in points],close=True)
        face=cq.Face.makeFromWires(wire)
        planar_faces.append(face)
        sewing.Add(face.wrapped)
    if not planar_faces: raise ValueError('No non-degenerate triangles')
    sewing.Perform()
    shape=cq.Shape.cast(sewing.SewedShape())
    representation='faceted_surface'
    if SOURCE_INFO['input_watertight']:
        solids=[]
        for shell in shape.Shells():
            solid=cq.Solid.makeSolid(shell)
            if solid.Volume()<0: solid=cq.Shape.cast(solid.wrapped.Reversed())
            solids.append(solid)
        if solids:
            candidate=solids[0] if len(solids)==1 else cq.Compound.makeCompound(solids)
            if candidate.isValid() and len(candidate.Faces())==len(planar_faces):
                shape=candidate
                representation='faceted_solid'
    if not shape.isValid():
        # Explicitly represent troublesome nonmanifold edges as separate faces.
        shape=cq.Compound.makeCompound(planar_faces)
        representation='independent_faces'
    shape=shape.scale(1/construction_scale).translate(tuple(center))
    return shape,{'representation':representation,'degenerate_faces_skipped':skipped,
                  'construction_scale':construction_scale,
                  'sewing_tolerance_original_units':1e-7/construction_scale}

def describe(shape):
    b=shape.BoundingBox()
    return {'valid':bool(shape.isValid()),'solids':len(shape.Solids()),
            'shells':len(shape.Shells()),'faces':len(shape.Faces()),
            'bounds':[[b.xmin,b.ymin,b.zmin],[b.xmax,b.ymax,b.zmax]],
            'solid_volume':float(shape.Volume()) if shape.Solids() else None}

def export(out,validate=True):
    start=time.time();out=Path(out);out.mkdir(parents=True,exist_ok=True)
    shape,metadata=build()
    state=describe(shape)
    if not state['valid']: raise RuntimeError('Constructed BREP is invalid')
    shape.exportBrep(str(out/(PART_NAME+'.brep')))
    shape.exportStep(str(out/(PART_NAME+'.step')))
    report={**SOURCE_INFO,**metadata,'cad':state,'step_unit':'mm',
            'source_physical_unit':'unknown','coordinate_policy':'preserve original numeric coordinates',
            'code_kind':'standalone embedded faceted geometry','source_modified':False}
    if validate:
        reopened=cq.importers.importStep(str(out/(PART_NAME+'.step'))).val()
        report['step_reimport']=describe(reopened)
        if not report['step_reimport']['valid']: raise RuntimeError('Reimported STEP is invalid')
        if report['step_reimport']['faces']!=state['faces']:
            raise RuntimeError('STEP transfer changed the face count')
        error=float(np.max(np.abs(np.asarray(report['step_reimport']['bounds'])-np.asarray(state['bounds']))))
        report['roundtrip_bounds_max_error']=error
        if error>max(float(np.ptp(decode_geometry()[0],axis=0).max())*1e-5,1e-6):
            raise RuntimeError('STEP transfer changed bounding dimensions')
    report['seconds']=time.time()-start
    report['status']='SUCCESS'
    (out/(PART_NAME+'_report.json')).write_text(json.dumps(report,indent=2),encoding='utf-8')
    return report

if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output-directory',type=Path,default=Path(__file__).resolve().parent)
    parser.add_argument('--no-validate',action='store_true')
    args=parser.parse_args()
    print(json.dumps(export(args.output_directory,not args.no_validate)),flush=True)
