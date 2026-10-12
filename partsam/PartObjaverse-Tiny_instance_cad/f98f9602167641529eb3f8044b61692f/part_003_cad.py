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

PART_NAME = 'part_003'
SOURCE_INFO = {'source_path': '/data/home/cuiyuehan/project/mesh2cad/partsam/PartObjaverse-Tiny_instance_stl/f98f9602167641529eb3f8044b61692f/part_003.stl', 'relative_path': 'f98f9602167641529eb3f8044b61692f/part_003.stl', 'source_sha256': 'ca81a46426aa66a801864fc8f4a636c6ca47de1c62cfc5b534232153cb41e7b0', 'input_faces': 272, 'input_vertices': 178, 'input_watertight': False, 'input_winding_consistent': False, 'input_bounds': [[0.18378201127052307, 0.09789325296878815, 0.18745118379592896], [0.37229394912719727, 0.17438887059688568, 0.25986555218696594]]}
GEOMETRY_BASE85 = 'c$}qK3shEB7QP6X5Q-v!`M`@hl7J6<q~h!1D-A^~k%uNfB7~KwKt5Bi4-ns#@Ap+x5f!nTbVTi@h$xtbshLf48_mXQHQDsAiEQrK-~PvYnpkVr%)i!N`#ay=XYYN_+56o4|9@PJr&oZ2Pl!^d__orikwW6D1Sr$evvVh=rRQ|WnljTvX-K^Ixb^DT_~CI$9?CRjcIbrkoV4uFC^fWqMvu@4H8f*#c5ZfRR?6h;3F(3#ocdx;y3OZgrcOz>$B##L?-8MPX&0f+QUAw}kDY=Ro`1HVtzE@K-xXTDKlzf-%Fl~s{$6+D&ES0!uV-gf2yJ{_B=Z^fX>1OkP1ju~TAn7qK10ZlnlK0RUjFeE+1L2P|EUGApL+Ks>BnGig)SoA`ZoF<viE5W`|mePe#}@CcF9|%xN78R8k-@p=ScT`yNs@1+<KA5E#ruHO-UnO&y68o@f}ON)vB_T#@^eA*N%ZVv$KwqE`+`L>T|N6{2eql`eaIRwYDQ@tQCDiT0d8QhORH_@E*+{YQa7#fp}}62k~b0SCYN;<*D<O*S)VKd-d)&#OvlaurFM3jQAz+WBm=hxwQCC6z>w^8sh^oZ&%xL8qc3uMdL9+#GA(sAkRGT%E_^nr2DpmeZ^ejt+$^gUW-3O_C^(W?Sp*ct?={UUEOfMIR)^uH5vZZdbr=3HM0HLbGYADYbATD>PO^vvOdKzZ<NwHTOIddUyl0`@2WqMc=gI??C-v2$am~j+FyMl?6rjE@N-}$?XTvYK)lf*RPv*IegNzHQK%Hx%umMpuKyVJhaRUoG@Fj3y47}kLcEcs5U<s5jym_fh4qg2q&io_V6S9<hV{Po4DqgJuvfHSWIt1?sm_(%_ocYT)0wFMn#&i+Zslm|Q_W}2CG5`?iFbJoBHs1Q4-#)JEg(Odc~9o&HUVGW5BvFi0{q;8e|257%-@86bIAmWSNb$XKYy4+>+RYWf&8OK<9>&xVt+39(K;w2!RsaCiMKq)5wG<Rf&b5DOMY}C8|Q;>TljOGMxD$p#s2;pfqZ|xgL*g$UQcQdzRoh#!=_BcYtcpWV<x?TzFs~9e6K51pGsxSdx$?z;?>R;)vas&eB8&fBI;A^Vlet~KX`LeCH1KuI1GH-4XC3w-Kg)Z+w0I@gFXV^`H6Du??%+k{+rn6Bu|_JiQx6nTd*(iBme4H@YW;W!@m19^y8{H^kYbk#9KXX;k;;aAN-<X@~>QNMfO@acq`)~`PXj1j~+GTeHwdI;5_`a4Ex%C1o39{KT6RrXV9mM!5ahD(E1xSQ?V~G@sc0)crN;J%USq&q8s-8$8lJ9qk?$7c>_F;zG#QMM^zH9+*eUo52v91>s29c=gH{Dd$3n_eJJ_YeDQoT`=wOVxOf89vzfdM`x@$!`BBfn|Bk5=Z?)`(`rlMYymdVt{jzj9{4Cff@%o}s@Dp%M;?-q)(T_F1;pcS+Ul?(j#&@EyJ|`xi&i1z_-g>Vw)~BQ+>f`6$5^w$SC-hNqAIXolVHNRunsym=Jqznu4SOv!8h#!P!+IWpy;-@Hc%!5m&&{qMq8_TY5wHDq9`Q!AJn(r%GT;6N?YnxTNb=*lP=I=<E<rw{_u_e-3VZF+VdC|=Uc_5<m*Cuv{gQYy?k3f_D<Ko-RPa~CE2naZ*MoWyucUn|+n=n#^XR2-C41v^7@k|n-+@0;PW@txfgd#syteUk>KAJ#;%bNgDcPG3hm#-If}dr3?_Vgc`bE7DXdF2J&*kxNqTe&TiC2f7Lp~Yctr7mjn~5#Rzg_~~RR!L)xE;=)x7g41Lil-S5cxM(9)+LyeZ=cmD{*eT243s;2Ju=>EBOByyjcof+1Y{o8y4HUP9yH=+c+ovr(pdf%izE3bmFyu{#gHM=Oufs)RWf7EI2RO>t-b0OUkN|&z1{Vf3MD1&$X9fKlf|O$E@px{qhUELVDRX)Mv^qJXab75wG6N!}&k>Rn+I%RuXR{eol3zsI4VGuBbJr&wzHsYl&~7K9|GZ^bZ3c?@zpv%l1>(5bruZ5dHf`7S5%Y)*|lC7U<vIJ#lW7y)N<A_WJ0T8M`Gv+Jar^$B07Y*>@%S^f>IbPWxc*t%2VGd)Jk)t2D1eE}b(*!_7E1PK3+6Pa2-1BYI1`zP=3aE#3Rb{IXHt2M#A*F9ok|hkq+PR^qjd@Nb?NC-M4QXK-J;Q)Ip{9{%Giz*jwmbvu}Yb@Qu2KC7O@_m1P>l~drgMjMDX4)%rpnCp@sZTdl+hmAg#?A60TSpUF3Oa9e$u($3<UZXf8K1KZmeUInhcRh&L287@}WF&YsrYG!Im!VGX?!<eqZ$HV8p0x*c=ru^Px9a?a?>QcWCI3nx+YgvUym|dD-e)f4;ap0XFY#*Ers%KOg~VGGH>tl|?<b;v$Aee*d!g@|<l}u{_Y%oopEHE~7}J)@_Vd_($~xkWw?@+Wqf}kOd(N5d#Jk2t;hcQzeVkX(2JUyoVDxnh=1Y$w?!DW1583hq-YZ@|0Y8nu!+Va2`&EvD*N(gb`<{DYA9xaew#8%LmrO$)ws;45PH&68+t45N^OOnul&6t@Xf@8gA@3s3{j*T#yLO<D{sP{$3EzK}jqtB^Iwjk0oe2N=%-`7#`@M*39ytyEd@%O+D(+W%s0{v<bHwYDa9>JsnY0c@QcJA=fpV<F-#^3q-ml51hjQ@xBJ7v$i~Ti9&q?cS7{xfp{4YxDW~3fPKNek<?n^I8t>_mg{o2wiC@Vy(FTOh2-^!H$B_q}GQ;Q(Q$E|<=r<RFb|Er%`I(P5<|NhjX**S>&7|416<4jwgqjiT)VH|7A2wR4-ev0uEwsg0pH|t)EU$$koEz?-P#JJd&gJL;Z?`J%aa~RC}NyaYDA(?d&<Ic8p;rLxRw!jN)na}a(bL^Mdm+%?GdKlwm_Bo36GmMKkx4o?QG45bXM~>f-V+-tM%R^iWLVGaIw<VAB%Hy0CaO`2cuETgu1rD<%+?F=1|G-%MHuea|d4ywlaZVz)J**2Ex8b?LtXnc}XiFpZ*NA-y{E98BY+1^B3FBa%+mv-P#_McZ%k$Rq9DxIE3F0_G97EtOwru8kn|aPU_9c8aVf`56?Y3;=dE0o7!2Y&0<~WTxMj-E**t<m535++{vXT95WMA7khKSXibqmJ2E%SKa=JB2h{F*JR+23mRC9t0@4LGj`oRdGt7CDS#{Ve0<wya=(E7;d-99!hjnsqD2vuv5kdClaU1YT@Q0sAXpUjlpEQjhbh$2s|NY>`76>j{iobF6l(A7`9nOD@OH<=6sy+ERz()ZrN3>`VBZ$ohH4?bv5~))9;+*^<R^vN%Q#&k=J|S&wHt)s}3Ym(6nouC0GldF~k2V;R@hkJD|L!Et7A41rzB@1H-l_1zeb70-G!<J!)pIkwE@_;We7z~Up$kh-iNX1s@E?PC2p<J!*cc+O!Y>!%sFwIx)+c_VZ<<J!*c+Rnp;wk+cNSj6`*hjSG<`?9Xj_(fY@;Cx@;Tm@DY@d!m;A)HfNzBh4?2J4-Sr*UpmSWjl`%dsA19l$ulmUNDv&anlq?Rm6^V=rdC%z+Ia3;n7C@8Ge}>m7JEkA>dqzz29N^ack$#ABh?IB*G%g<k2vhj}dYQpTe1M4x%H_GH|eulcd|X55^w`Lp(8+=Q<Mvi4`(l&>{p9mqJCulcZU$hZw(^J4A8IE=3;ti2e=+0xaP;fy;u#yxBq!nmtr9A!&?#yuS4KDP8_9OW4Iv?ZExAIG?xErS^Mbc`bvyz>lV&OH|I1hI@Gd8{iqYZ6(HVk~%Z7SCdw$m1O5(pZmU>^>7GF-~)g-RI&Y=EQh9b7NSiG8Viz3+6B$;~0zcU?Jmp9*Y_hwY5}vP-6m%nmfeT-8Ct&sL=y_-Ce^1i<;ie*WEQQu;_sueBIq60*jt8_`0Dy=q1r(yZE}h2L%>AxreX2dsbla5w+#4F)tSP`;@yTeOTP@NA4PK$Re<_<^x#-cJ_!ri@?sF@?#O$*@NCJ0(&YCdRAajPwrZB)|SxD+H=>U(9T+Q*RIgc+IH8v(9T|P_lD5U-f{Pm(9T|S_ny$s-gNh>yQbn5xweFM)}Ff--8Jg0VRwB`RQ|Kp<6=DO1bEi=SNDUDPA}rlKfZrEQ~uiKoS9|&`uCT(xR{5;GtGYKsY8j}5mlo63zC(TAO'

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
