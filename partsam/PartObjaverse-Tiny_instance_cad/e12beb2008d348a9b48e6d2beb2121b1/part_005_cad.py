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

PART_NAME = 'part_005'
SOURCE_INFO = {'source_path': '/data/home/cuiyuehan/project/mesh2cad/partsam/PartObjaverse-Tiny_instance_stl/e12beb2008d348a9b48e6d2beb2121b1/part_005.stl', 'relative_path': 'e12beb2008d348a9b48e6d2beb2121b1/part_005.stl', 'source_sha256': 'cefcf8016e4f87f795d9424570db30488ce4387898c5cb2b09cf047edd3215de', 'input_faces': 348, 'input_vertices': 233, 'input_watertight': False, 'input_winding_consistent': True, 'input_bounds': [[-0.23622724413871765, 0.1422221064567566, -0.1443265825510025], [0.017923571169376373, 0.42679792642593384, 0.14713220298290253]]}
GEOMETRY_BASE85 = 'c$}r02UHbT8pj80SYj+_)EFJ>v!F3TRIFp{K@b%*_5ne$BiPWWW3SkIfk7jQ3J8dx2)wbPAokuEOEhkFO=1#DHtN3lzW>Y4c-(XL?7nmE`TyR}%YFBLGjnI&JNo++De5lptCrwb<znzxl?B0QWdwI&N@&ESQNu$cn~o2UauLdrH(t(M>lf(jKfpzpBFwObghmdJu(cL#ZAY}Sd5E?V6Cx%>1dSgyAtEHy@Lhw(Mus|kWLQvmsN;Qu=AND&qGv-7ai;h`zDhZ!pry1uYd3O!W?lzJN)>GVJD9v&Fg@RRucX_z*-c)7*J{PYn){2#wii(U;~sm>{bhLZkF5#j{@Sdt^W^<*r<nWe@X8NsQ!V|yeJ&dB)xyF1&HaVe?DZ)3G;@DxaMR1id-<L5Wq9eG@#R;!SLkz3Sm&?6i?6KnmnYr0O8pO6>*MrV4QqY0P2SgN9KAl(S!pvhkNS5nb(-E+wpqNG@*{a|Md%K*7lw^JL-RkGoNV^ezDiU#xmM}{OMlcyeKsk>GQP(gs)P7We|@ja>pEc_Uv-V6`3uq3`6#{0U#EHA;&th7vvX;^?r&-Sg1gP))gKD@eB1X_we;^)mCh6OWnz-qi_1Fmx>EnK-|YWd*MMaQEdBla@VegVFMF4wb;&QR<7<yTrFF@_zlpKG$7_k!d8+;!$xC;6y@F@O<5d3&A+#=`qRry93ytV{kyiCpE&c!Ap600+dhR!SxyvIu-_&|F6YM6hzzYLbBwEIaaH07q8K<_}-{Z9v*3T6#hVc9gdH!Pj9*x$W(~{;Xl($*D8u*mG{KZzg$!kuZFUFYri#wk4aqND2x4FLzFU@MT*U~>g;p5xx_hfT_30}CKkYeud+y|sF!Kvo{x^sUhR&Bqf|H8^tXZ4-&g+=VOYu54gC0n`vJ*@K=ma>;-zBB*iSiatat@V-MrBl}WsQ>(f&%=9Mf2m3Yj~~*5>rljI^=re)Yok*a*iBx9ml}V)%-mlruXEj2cU^DpFTv}7)ZJw6ugqR}fyR$$zs>$0FWs&lYwqu?zZ{YhWA5*)zxc|!E~nQX<*Jr>{`TP|dLL>1TnS#gW&K?JbUJxqjdfi@9((<jbzMUD`gDASan`#1<r}_Jx2e8-JwC<$e7F@KuUav@k5#f+yw-XWUGH-Ld2wd%+?NE&H{IgD58?AL@(JC)oL+SL58~3y{dJoMohQ1tUy`}M(15)(E_<J4p4o%>dav!Sn)_?;dZ2ZlT5vA!19z|w-1W|+@m~x)#dWb+y>AbygL-=6PK(ES<@J{in!U7t2d}GFhjhEi%kavR=joRI_hR@ua($L;?yta$+jggz`>S5hX#VOt*B$2m8oZusou@i%6y2wUn>fDG-wx3H>nz~@yVKL`CNILvoyODsMV$PY``3TV_m_39hwUaW!Rry3hw1M;?vs~)+jNrVS)J?Y^pf}PTzdbie7xC<eV+5aRHsp<*=t*Kc>YUczp<OVu#LU^!a9ypuiFj!+$+3ZEh(D3df*<<zht+Ac9YlPwa0JhIBG?g@HnMo`8r+JGRtoA8oW6Ar!4ySN;V$H9ztG@Uw_DM@}kCGTHs6TlAae*y@fISyrH{9@Oc0)!HarBs;AO7g?&O*+K08U;yHGcSKy^?IXTqdb0T{Y;}`77u$#OFFC_%idey>_<khle_`I$BD~<2;I=uAz9y^T}`<Sj{vCzin?XHd4c9U1&mHEABKJw0s{M=e%3STedA5ed%7u?`|w^Dy`Wl!>wREO_t^FsK1gIAnBxH{MWi>mC?8c?0pfuHbx3a`TpUq)#(-#Odp{;9W$=JUMXcD{b#MQ`?6kwB`yKB_T!xlUPrj`can>xI|g)rR4`-lJ8>3r{@wxjJ|}KL^0e@M`Zonva<KCqJjB?c#C5Z_x2_df@<jvDa!kUQ&%;*n4c{{bX(u-?su1$V+YP{JG!yTf73VZb;zI9od$=s@LS>TcgAgnqRe&<n`CdbRU#|J#II9=?!~vRC}&x#B<uWgd%JB`DFDK-e=)uct!c_2=)InllQrlHgui{BL;APcm-YzJV4_MtGbcb9{AGdDhcDL{!TAGWUnu)NA;IFxwBt!mX5npFq+n-`p()%-fK4>-=yI=W-r4F(I4BnJ`d^sBcJKd`;Rb_&qH_>Ub^c==b@T&oxHenC9kXGV!l7YD^CCN0oQ-8Un2QCsk}dg<<UGvH<A7K3XQLx$~$QG8oU-i_YnPix*PkpE%^JI+j1T!H=drObzvA^Uoi_TUUFftN8h94qOQ^D`=8K0iT8~Wm-&8NtO<F!{dlUgkaNo7HF!C(E{&tNIKPL+k8<UGxZqE^zMNix7e=P>^_3M%Uf%xt7}cQ;zBj>3r=$~f9Q)VYWAUNWct3nr!fy7;htF^DILY7HO<si;0<Gi7Wj5U;e-6(Bv-^?Pnq1(0{$%B&RJZ#@x&P#Qe4W0XMc0Kkv?@I>D_e?jedZ6dcpY9#DNV;+$|z1=ieAI}q>C3F7vX94x0F&GAK#5nv&>$G*C)qk)4Vz#BCpk~$Jg(uE;LVNP!saXiw*qz*|nm@>+n*G2}kL;O-PTY`TQ*LaZlbz^U>B_-9>d<AIJAcn;(z!I*7b9?L1!>w+3aJy#g;Dsz}FIbn#{X(+NIaJ%6V0^@FeJey%_EWIwhUjV~X|A+I(_;{CaHIPVY3i<1{qGq|2h<{UA51zw7}L+7D%C4iofB)8_g54;Sc@tt0U*B>9JI*0*-;^^O-1oHXpGY#L<*sJhb>&tu`?brEvQyI$pfOwep6Q|dl{!Ij(pK9GG^5WEw`20C$<9!KUar)GGyiZ;{NZ)Ifo>lm{#V3m9@ANvn-1-X5Uz&EEzK2N<7jgaX_+{BmUWJzq7pL<_xRk-)+dlE)<Gv=J&qH__UYKj+@$U`iak|Xq?>kd}q5e)UbY-uM@a6tV8@7<ot53&Qf6|fb4=+3Y_3hMO8@Ox(t#8U^u0tO`KJM_sRQQg2xc=LU(Dxx>Xfxj5mjA-{eRvsOpW(~(jLu(6{kJ^g=f*a1R0k!b_ZsS7aUY)#ZYB6Uhu7exm%%ho_2uG~^zRo_`S*ug{rEltufuDH%JO|=_i*w;WH{f~I@jfW7+!{#Jr$a#Yztpb<9}6-@7MMmzAwXT@On};o=<~u3u)cYCi8R7T{k|j;8l3JAcV)yO;c!|eJ1kf-mbvUC-72V_G<okzP~4~|C+`LT~41T*zkKPynO9P+PCHV0SRWW{G`&psuo(k^qv1Ls%JjFFF$`fo$4{<H$I=WOg@hA3cRwfGR<FEF>noKpcl<YH|FDS`BnOA-Jr+k%L#(fN(%16h#=EX(uOo%&V2t*(xbfotDmGjy;}XhKS}@Kn8O1{yN_mYJn~y`JU9dy3JwAHL-q$7=?m@$?uo1m?g_4gtOl+FuIgyzkmZrpz~#XekRO99fGZ-agDZmFk)MFw!Ih9Tz?Hz2ku|}U!5=wV6=W@BO>ix+4OtIt1N$TWz(#%r_6H9{jsOn?2O+-$2Z47XuYiqw2;K$WgZv)62fP=#8@v}h68R0-NEtj5JP0`eJP6zy*$ZrBeQ<AZ1EdIU0IrR!0<MCZ)<!e9A<_nJ2=0UQ2m7OTeb5XZj0^$~28SVcfp?)sVaUDUFz_hkNbo4|5ab~65O7~)Z*Xs{xi6Z*jgYm$wXwEFXa)x$`+)mk4FPBd4@HK7!!W<0Xa)~M4gn7X2O|4|`{J_$kpbWUjAd{eM{DP3osb>CMs@@n*%{mh*%r;<_Gku6Xa;|QW^flYgS(*_+yl*EA4l_cwANrFTY-JRJ&-L-f7=4%8R=yj-wU5<WOLITnqyu@HZ#q$8Rl+eQ`1_SVtqz>nAYoo8ni(+MtXo7gPkvfU64(|F5n`_X5b>=V#wy;V&D=;FK`KPNn{IfNpNXoD{yJ>2gugo55OOy8C(|W4K52VgKP;d11^R999#<QhV%rxfr}$Q0~ZGuMScn{3U);{0lR{ouO_H{8)Q3V6L33l2jr*V4&aW+&%hnQospj4&fu=d&%s^6-H|Q9-N9cXy}?HMfQ{?~{u1o`+fEp}6F%Eu<Jvc_W8->0?P%8>?E;#?H<3E{Ciph;5%@OvD)KJ)D!2f730wfqMjioYgLfd4z&pUpk!!%q!PAjngQtVXBFBTrf`gHx!NK5g<Rox7SV1lXE8vaDZQzaI6y!m03iufEH25@XeGJXu6KDqKBX5H9!RL^-!RNra$gAL7upL<dwu94<+2AyAEOG}p7Q6zv9J~TN3ppJ;3p@om7CZ$UfeZ#mfTtnD!PCHVkqUS&cs+6>cs)1~nF3A(XCaS)kD=CCXa=XF8JvmC2WNs0BhP^kgENr1;0*A7q#e8;oPbONCxEviW5HX&>yRtJ>%hy9v%t&1i;+{ni^21e5#agYCCF*uCE!)ax!_gc&B*oO&EPm>A~+75jLZUOq1MT02FD;X!I`LU3^D_pfjY(@6Tk_mR}69;cpd5zgIo+=jP=JLmw=aGoiWJG;LTW%!Fi5$(a~-oZ-H-s?;-Di?|~m9uYn(f3z28Rh2YD`9PnlEQRGhWQSd%wG<Y9)Epi5UEqEq!9C#*p0&+Nb0(cB^B6tjVvZF0R&OuHD&jHUvGdK!492^CXM2-VTf~O*9fTx0IBcs8y!7GtF!7ITkG6$@J4<OHi4}dk~HLwOgg}ehk1wN0w1wIcxgS-en13rmn@Nr}w*vLcR<KR@}c5o_q6LJxF5$e7P&EO5ldEgD;EocU>Mn-{GgO?&B!Arpl9L?Xy#nrvYfBG+a|9&aPL#yRK?7jP!)}K+#f4RXi)?YuW`1=$yp7k6LaISO`#TnlKg?|AKZd|P'

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
